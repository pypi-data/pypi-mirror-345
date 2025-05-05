import json
from pathlib import Path
from uuid import uuid4

import requests
from appdirs import user_config_dir
from humps import camelize, decamelize
from requests_toolbelt.multipart.encoder import (
    MultipartEncoder,
    MultipartEncoderMonitor,
)
from tqdm import tqdm

from .constants import APP_NAME, ORGANISATION
from .exceptions import (
    GWDCAuthenticationError,
    GWDCUnknownException,
)
from .logger import create_logger
from .utils import split_variables_dict

logger = create_logger(__name__)


class GWDC:
    def __init__(self, token, endpoint, custom_error_handler=None):
        self.api_token = token
        self.endpoint = endpoint
        if custom_error_handler:
            self._apply_custom_error_handler(custom_error_handler)
        if self.api_token:
            self._check_api_token()
        else:
            self.public_id = self._obtain_public_id()
            self.session_id = self._obtain_session_id()

    def _obtain_session_id(self):
        return str(uuid4())

    def _obtain_public_id(self):
        config_file = Path(user_config_dir(APP_NAME, ORGANISATION)) / "config.json"

        def write_new_config():
            uuid = str(uuid4())

            config = {"public_id": uuid}

            config_file.parent.mkdir(parents=True, exist_ok=True)
            config_file.write_text(json.dumps(config))

        if not config_file.exists():
            write_new_config()

        try:
            return json.loads(config_file.read_text())["public_id"]
        except Exception:
            write_new_config()
            return json.loads(config_file.read_text())["public_id"]

    def _check_api_token(self):
        resp = self.request(
            query="""query {
    sessionUser {
        isAuthenticated
    }
}"""
        )

        if resp.get("session_user", None) and resp["session_user"].get(
            "is_authenticated", None
        ):
            return
        raise GWDCAuthenticationError

    def _apply_custom_error_handler(self, custom_error_handler):
        self.request = custom_error_handler(self.request)
        # Also has to wrap _check_api_token in order to catch authentication errors
        self._check_api_token = custom_error_handler(self._check_api_token)

    def _request(self, endpoint, query, variables=None, headers=None, method="POST"):
        if headers is None:
            headers = {}

        if variables is None:
            variables = {}

        variables = camelize(variables)
        variables, files, files_map = split_variables_dict(variables)

        if files:
            operations = {
                "query": query,
                "variables": variables,
                "operationName": query.replace("(", " ").split()[
                    1
                ],  # Hack for getting mutation name from query string
            }

            e = MultipartEncoder(
                {
                    "operations": json.dumps(operations),
                    "map": json.dumps(files_map),
                    **files,
                }
            )

            encoder_len = e.len
            bar = tqdm(total=encoder_len, leave=True, unit="B", unit_scale=True)

            def update_progress(mon):
                update_bytes = mon.bytes_read - bar.n
                bar.update(update_bytes)

                if not update_bytes:
                    bar.close()
                    logger.info(
                        "Files are being processed remotely, please be patient. This may take a while..."
                    )

            m = MultipartEncoderMonitor(e, update_progress)

            request_params = {"data": m}

            headers["Content-Type"] = m.content_type
        else:
            request_params = {"json": {"query": query, "variables": variables}}

        request = requests.request(
            method=method, url=endpoint, headers=headers, **request_params
        )

        content = json.loads(request.content)
        errors = content.get("errors", None)
        if not errors:
            return decamelize(content.get("data", None))
        else:
            raise GWDCUnknownException(errors[0].get("message"))

    def request(self, query, variables=None, headers=None, authorize=True):
        all_headers = {}
        if authorize:
            if self.api_token:
                all_headers = {"Authorization": self.api_token}
            elif self.public_id:
                all_headers = {
                    "X-Correlation-ID": f"{self.public_id} {self.session_id}"
                }

        if headers is not None:
            all_headers = {**all_headers, **headers}

        return self._request(
            endpoint=self.endpoint,
            query=query,
            variables=variables,
            headers=all_headers,
        )
