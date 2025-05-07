import base64
import configparser
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional

import requests
from frogml_storage.authentication._authentication_utils import get_credentials
from frogml_storage.authentication.models._auth_config import AuthConfig

from qwak_inference.configuration.session import Session
from qwak_inference.constants import QwakConstants
from qwak_inference.exceptions import QwakLoginException


class BaseAuthClient(ABC):
    @abstractmethod
    def get_token(self) -> Optional[str]:
        pass

    @abstractmethod
    def login(self) -> None:
        pass


class Auth0Client(BaseAuthClient):
    _TOKENS_FIELD = "TOKENS"

    def __init__(
        self,
        api_key=None,
        auth_file=None,
    ):
        if auth_file:
            self._auth_file = auth_file
        else:
            self._auth_file = QwakConstants.QWAK_AUTHORIZATION_FILE

        self._config = configparser.ConfigParser()
        self._environment = Session().get_environment()
        self.token = None
        self.api_key = api_key

    # Returns Non if token is expired
    def get_token(self):
        try:
            if not self.token:
                self._config.read(self._auth_file)
                self.token = json.loads(
                    self._config.get(
                        section=self._environment, option=self._TOKENS_FIELD
                    )
                )

            # Check that token isn't expired
            if datetime.now(timezone.utc) >= self.token_expiration():
                self.login()
                return self.token
            else:
                return self.token
        except configparser.NoSectionError:
            self.login()
            return self.token

    def login(self):
        try:
            response = requests.post(
                QwakConstants.QWAK_AUTHENTICATION_URL,
                json={"qwakApiKey": self.api_key},
                timeout=30,
            )
            if response.status_code == 200:
                self.token = response.json()["accessToken"]
            else:
                raise QwakLoginException(f"Error: {response.reason}")

            from pathlib import Path

            Path(self._auth_file).parent.mkdir(parents=True, exist_ok=True)
            self._config.read(self._auth_file)

            with open(self._auth_file, "w") as configfile:
                self._config[self._environment] = {
                    self._TOKENS_FIELD: json.dumps(self.token)
                }

                self._config.write(configfile)
        except Exception as e:
            raise e

    def token_expiration(self) -> datetime:
        if not self.token:
            self.login()
        tokenSplit = self.token.split(".")
        decoded_token = json.loads(_base64url_decode(tokenSplit[1]).decode("utf-8"))
        return datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)


def _base64url_decode(input):
    rem = len(input) % 4
    if rem > 0:
        input += "=" * (4 - rem)

    return base64.urlsafe_b64decode(input)


class FrogMLAuthClient(BaseAuthClient):
    def __init__(self, auth_config: Optional[AuthConfig] = None):
        self.auth_config = auth_config
        self._token = None
        self._tenant_id = None

    def get_token(self) -> Optional[str]:
        if not self._token:
            self.login()
        return self._token

    def get_tenant_id(self) -> Optional[str]:
        if not self._tenant_id:
            self.login()
        return self._tenant_id

    def login(self) -> None:
        artifactory_url, auth = get_credentials(self.auth_config)
        if hasattr(auth, "token"):  # For BearerAuth
            self._token = auth.token
            # Remove '/artifactory/' from the URL
            if "/artifactory" in artifactory_url:
                base_url = artifactory_url.replace("/artifactory", "/ui")
            else:
                # Remove trailing slash if it exists and append /ui
                base_url = artifactory_url.rstrip("/") + "/ui"
            try:
                response = requests.get(
                    f"{base_url}/api/v1/system/auth/screen/footer",
                    headers={"Authorization": f"Bearer {self._token}"},
                    timeout=60,
                )
                response.raise_for_status()  # Raises an HTTPError for bad responses
                response_data = response.json()
                if "serverId" not in response_data:
                    raise QwakLoginException(
                        "Failed to authenticate with JFrog. Please check your credentials"
                    )
                self._tenant_id = response_data["serverId"]
            except requests.exceptions.RequestException:
                raise QwakLoginException(
                    "Failed to authenticate with JFrog. Please check your credentials"
                )
            except ValueError:  # This catches JSON decode errors
                raise QwakLoginException(
                    "Failed to authenticate with JFrog. Please check your credentials"
                )

    def token_expiration(self) -> Optional[datetime]:
        if not self._token:
            self.login()
        tokenSplit = self._token.split(".")
        decoded_token = json.loads(_base64url_decode(tokenSplit[1]).decode("utf-8"))
        if "exp" in decoded_token:
            return datetime.fromtimestamp(decoded_token["exp"], tz=timezone.utc)
        else:
            return None
