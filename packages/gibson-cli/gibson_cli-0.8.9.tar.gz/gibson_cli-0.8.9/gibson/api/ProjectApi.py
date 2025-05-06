from gibson.api.BaseApi import BaseApi
from gibson.core.Configuration import Configuration


class ProjectApi(BaseApi):
    PREFIX = "project"

    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def list(self):
        return self.get()["projects"]

    def create(self):
        return self.post().json()

    def database_schema(self, uuid: str):
        return self.get(f"{uuid}/schema/deployed")

    def lookup(self, uuid: str):
        return self.get(f"{uuid}")

    def deploy(self, uuid: str):
        return self.post(f"{uuid}/deploy")

    def mcp(self, uuid: str):
        return self.get(f"{uuid}/mcp")

    def schema(self, uuid: str):
        return self.get(f"{uuid}/schema")

    def structure(self, uuid: str):
        return self.get(f"{uuid}/structure")

    def submit_message(self, uuid: str, message: str):
        if not message:
            raise ValueError("Message is required")

        return self.post(f"{uuid}/conversation", {"content": message}).json()

    def update(self, uuid: str, name: str):
        if not name:
            raise ValueError("Name is required")

        return self.patch(f"{uuid}", {"name": name}).json()
