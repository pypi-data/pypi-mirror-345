from typing import Dict, List

from mcp.server.fastmcp import FastMCP
from requests.exceptions import HTTPError

from gibson.api.DataApi import DataApi
from gibson.api.ProjectApi import ProjectApi
from gibson.core.Configuration import Configuration

mcp = FastMCP("GibsonAI")

# Note: Resources are not yet supported by Cursor, everything must be implemented as a tool
# See https://docs.cursor.com/context/model-context-protocol#limitations


def error_handler(e: HTTPError) -> Dict:
    """Handle HTTP errors from the API"""
    status_code = e.response.status_code
    message = e.response.json()
    if status_code == 401:
        message = "Authentication required. Instruct the user to run `uvx --from gibson-cli@latest gibson auth login` to authenticate then try again."
    return {"status_code": status_code, "error": message}


@mcp.tool()
def get_projects() -> List[Dict]:
    """
    Get all of the user's existing GibsonAI projects.
    <IMPORTANT>
    If the user mentions a project by name and you don't have the project UUID, call this tool.
    If there's a .gibsonai file in the project or workspace root directory, assume that the user wants to use that project and don't call this tool unless there's a good reason to do so.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.list()
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def create_project() -> Dict:
    """
    Create a new GibsonAI project.
    <IMPORTANT>
    Before assuming that the user wants to create a new project, look for a .gibsonai file in the project or workspace root directory.
    If the .gibsonai file exists and contains a project UUID, call get_project_details to get the project details and ask the user if they want to use the existing project.
    If the .gibsonai file doesn't exist, but the user mentions a project name, call get_projects to check if a project with a similar name already exists and ask the user if they want to use the existing project.
    If the user explicitly states they want to create a new project, call this tool without confirming.
    If you call this tool, ask the user if they want to update the .gibsonai file (or create it if it doesn't exist) with the new project UUID.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.create()
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def get_project_details(uuid: str) -> Dict:
    """
    Get a GibsonAI project's details.
    <IMPORTANT>
    If there's a .gibsonai file in the project or workspace root directory, assume that the user wants to use that project unless they explicitly state otherwise.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.lookup(uuid=uuid)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def get_project_hosted_database_details(uuid: str) -> str:
    """
    Get the details for querying a GibsonAI project's hosted database.
    <IMPORTANT>
    This includes necessary context for an LLM to understand and generate code related to fetching or modifying the data in the project's hosted database.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.mcp(uuid=uuid)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def update_project(uuid: str, project_name: str) -> Dict:
    """
    Update a GibsonAI project's details.
    This currently only updates the project's name.
    Returns the updated project details.
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.update(uuid=uuid, name=project_name)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def submit_data_modeling_request(uuid: str, data_modeling_request: str) -> Dict:
    """
    Submit a data modeling request for a GibsonAI project.
    <IMPORTANT>
    This tool fully handles all data modeling tasks.
    The LLM should not attempt to handle any data modeling tasks.
    If the user describes a data modeling task, call this tool with the user's request as-is.
    Again, the LLM should never attempt to directly handle data modeling tasks when working on a GibsonAI project.
    </IMPORTANT>
    Returns the response from GibsonAI's data modeler.
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.submit_message(uuid=uuid, message=data_modeling_request)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def deploy_project(uuid: str) -> None:
    """
    Deploy a GibsonAI project's hosted databases.
    <IMPORTANT>
    This updates both the development and production database schemas simultaneously by automatically handling necessary schema migrations.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.deploy(uuid=uuid)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def get_project_schema(uuid: str) -> str:
    """
    Get the current schema for a GibsonAI project.
    <IMPORTANT>
    This includes any changes made to the schema since the last deployment.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.schema(uuid=uuid)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def get_deployed_schema(uuid: str) -> str:
    """
    Get the deployed schema for a GibsonAI project.
    <IMPORTANT>
    This is the database schema that is currently live on the project's hosted databases.
    </IMPORTANT>
    """
    project_api = ProjectApi(Configuration(interactive=False))
    try:
        return project_api.database_schema(uuid=uuid)
    except HTTPError as e:
        return error_handler(e)


@mcp.tool()
def query_database(api_key: str, query: str) -> List[Dict] | str | Dict:
    """
    Query a GibsonAI project's hosted database using SQL. The environment-specific API key must be provided.
    <IMPORTANT>
    If you're not sure which environment to use, ask the user for clarification.
    Always use the correct syntax for the database dialect (found in the project details).
    Always wrap identifiers in the dialect appropriate quotes (backticks for MySQL, double quotes for PostgreSQL).
    </IMPORTANT>
    """
    data_api = DataApi(Configuration(interactive=False), api_key=api_key)
    try:
        response = data_api.query(query=query)
        return response or "Query executed successfully"
    except HTTPError as e:
        return error_handler(e)
