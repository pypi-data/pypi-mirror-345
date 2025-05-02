from gibson.api.BaseApi import BaseApi
from gibson.core.Configuration import Configuration


class DataApi(BaseApi):
    PREFIX = "-"

    def __init__(self, configuration: Configuration, api_key: str):
        self.configuration = configuration
        self.api_key = api_key or self.configuration.project.api.key

    def headers(self):
        headers = super().headers()
        headers["X-Gibson-API-Key"] = self.api_key
        return headers

    def query(self, query: str):
        return self.post("query", {"query": query}).json()
