import pprint

import requests

from gibson.core.Configuration import Configuration


class BaseApi:
    VERSION = "v1"

    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def base_url(self):
        return f"{self.configuration.api_domain()}/{self.VERSION}"

    def delete(self, endpoint):
        r = requests.delete(self.url(endpoint), headers=self.headers())

        if r.status_code == 401 and self.refresh_auth_tokens():
            r = requests.delete(self.url(endpoint), headers=self.headers())

        self.__raise_for_status(r)

        return r

    def get(self, endpoint: str = ""):
        r = requests.get(self.url(endpoint), headers=self.headers())

        if r.status_code == 401 and self.refresh_auth_tokens():
            r = requests.get(self.url(endpoint), headers=self.headers())

        self.__raise_for_status(r)

        return r.json()

    def headers(self):
        headers = {
            "X-Gibson-Client-ID": self.configuration.client_id(),
        }

        token = self.configuration.get_access_token()
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def patch(self, endpoint: str = "", json: dict = None):
        r = requests.patch(self.url(endpoint), headers=self.headers(), json=json)

        if r.status_code == 401 and self.refresh_auth_tokens():
            r = requests.patch(self.url(endpoint), headers=self.headers(), json=json)

        self.__raise_for_status(r)

        return r

    def post(self, endpoint: str = "", json: dict = None):
        r = requests.post(self.url(endpoint), headers=self.headers(), json=json)

        if r.status_code == 401 and self.refresh_auth_tokens():
            r = requests.post(self.url(endpoint), headers=self.headers(), json=json)

        self.__raise_for_status(r)

        return r

    def put(self, endpoint: str = "", json: dict = None):
        r = requests.put(self.url(endpoint), headers=self.headers(), json=json)

        if r.status_code == 401 and self.refresh_auth_tokens():
            r = requests.put(self.url(endpoint), headers=self.headers(), json=json)

        self.__raise_for_status(r)

        return r

    def refresh_auth_tokens(self):
        refresh_token = self.configuration.get_refresh_token()
        if not refresh_token:
            return False

        r = requests.post(
            f"{self.base_url()}/auth/token/refresh",
            headers=self.headers(),
            json={"refresh_token": refresh_token},
        )

        if r.status_code != 200:
            self.configuration.set_auth_tokens(None, None)
            return False

        parsed = r.json()
        self.configuration.set_auth_tokens(
            parsed["access_token"], parsed["refresh_token"]
        )
        return True

    def url(self, endpoint: str):
        base = f"{self.base_url()}/{self.PREFIX}" if self.PREFIX else self.base_url()
        return f"{base}/{endpoint}" if endpoint else base

    def __raise_for_status(self, r):
        if r.status_code == 401:
            self.configuration.login_required()

        try:
            r.raise_for_status()
        except:
            try:
                message = r.json()
                print("=" * 78)
                print("Raw Response:\n")
                pprint.pprint(message)
                print("\n" + "=" * 78)
            except requests.exceptions.JSONDecodeError:
                pass

            raise
