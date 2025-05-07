from typing import Optional, Union, cast

import requests
from frogml_storage._utils import BearerAuth
from frogml_storage.authentication._authentication_utils import get_credentials
from frogml_storage.authentication.models._auth_config import AuthConfig
from requests.auth import AuthBase

from frogml_core.exceptions import FrogmlLoginException


class FrogMLAuthClient:
    def __init__(self, auth_config: Optional[AuthConfig] = None):
        self.auth_config: Optional[AuthConfig] = auth_config
        self._token: Optional[str] = None
        self._tenant_id: Optional[str] = None

    def get_token(self) -> str:
        if not self._token:
            self.login()

        return cast(str, self._token)

    def get_tenant_id(self) -> str:
        if not self._tenant_id:
            self.login()

        return cast(str, self._tenant_id)

    def login(self):
        artifactory_url, auth = get_credentials(self.auth_config)

        if isinstance(auth, BearerAuth):  # For BearerAuth
            self._token = auth.token

        self.__get_tenant_id(artifactory_url, auth)

    def get_auth(self) -> Union[AuthBase]:
        return get_credentials(self.auth_config)[1]

    def __get_tenant_id(self, artifactory_url: str, auth: AuthBase):
        login_exception = FrogmlLoginException(
            "Failed to authenticate with JFrog. Please check your credentials"
        )

        # Remove '/artifactory/' from the URL
        if "/artifactory" in artifactory_url:
            base_url = artifactory_url.replace("/artifactory", "/ui")
        else:
            # Remove trailing slash if it exists and append /ui
            base_url = artifactory_url.rstrip("/") + "/ui"

        url = f"{base_url}/api/v1/system/auth/screen/footer"

        try:
            response = requests.get(url, timeout=15, auth=auth)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_data = response.json()

            if "serverId" not in response_data:
                raise login_exception
            self._tenant_id = response_data["serverId"]

        except (requests.exceptions.RequestException, ValueError) as exc:
            raise login_exception from exc
