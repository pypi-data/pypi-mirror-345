# server.py
import os
import httpx
from mcp.server.fastmcp import FastMCP, Context
from dotenv import load_dotenv
from LoginRadius import LoginRadius
import logging
import sys

logging.basicConfig(
    level=logging.INFO, # Or logging.DEBUG for more detail
    stream=sys.stderr,  # Explicitly direct logs to stderr
    format='%(asctime)s - %(name)s - %(levelname)s - SERVER: %(message)s' # Add SERVER prefix
)


mcp = FastMCP("DREX")
load_dotenv()

DREX_BASE_URL = os.getenv("DREX_BASE_URL")

lr = None
LR_API_KEY = os.getenv('LR_API_KEY')
LR_API_SECRET = os.getenv('LR_API_SECRET')

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
async def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    ctx = mcp.get_context()  
    await ctx.session.send_log_message(
        level="info",
        data=f"Greeting user {name}",
    )
    return f"Hello, {name}!"


async def init_loginradius(ctx: Context | None = None) -> None:
    global lr
    if lr is not None:
        return
    
    if LR_API_KEY and LR_API_SECRET:
        LoginRadius.API_KEY    = LR_API_KEY
        LoginRadius.API_SECRET = LR_API_SECRET
        lr = LoginRadius()

    await ctx.session.send_log_message(
        level="info",
        data="LoginRadius SDK initialised successfully"
    )


@mcp.tool()
async def get_token(username: str,
                    password: str) -> str:
    """
    Return an auth token by logging in with username/password.
    """
    ctx = mcp.get_context()               # ctx is never None for tools

    if not username or not password:
        return "No username or password provided. Skipping token generation."

    if not LR_API_KEY or not LR_API_SECRET:
        return "API Key and Secret are not configured. Cannot get token."

    if lr is None:
        await init_loginradius(ctx=ctx)

    try:
        email_authentication_model = { 
            "email" : username,
            "password" : password
            }
        response = lr.authentication.login_by_email(email_authentication_model)
        await ctx.session.send_log_message(
            level="debug",
            data=f"Login response: {response}"
        )
        return response.get("access_token", "No access token found in response")
    except Exception as e:
        return f"Error during login: {str(e)}"


def is_valid_filename(filename: str, ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".txt"}) -> bool:
    _, ext = os.path.splitext(filename)
    return ext.lower() in ALLOWED_EXTENSIONS


@mcp.tool()
async def file_upload(file_paths: list[str], uploaded_by: str, token: str) -> str:
    """
    Upload multiple files to the DREX API using file paths.

    Arguments:
        file_paths (list[str]): List of absolute or relative paths to the files intended for upload.
        uploaded_by (str): Identifier (e.g., username or email) of the user performing the upload.
        token (str): Authorization token for authenticating API requests.

    Returns:
        str: JSON response from DREX API upon successful file upload.

    Raises:
        ValueError: If any file path does not exist or has an invalid filename or file type.
        Exception: If the API response indicates a failure during file upload.
    """
    endpoint = f"{DREX_BASE_URL}/file-upload"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"uploadedBy": uploaded_by}

    file_payload = []
    for path in file_paths:
        if not os.path.exists(path):
            raise ValueError(f"File not found: {path}")

        filename = os.path.basename(path)

        # Validate filename
        if not is_valid_filename(filename):
            raise ValueError(f"Invalid or unsupported file type: {filename}. Valid example: <file>.png")

        try:
            with open(path, "rb") as f:
                file_content = f.read()
        except Exception as e:
            raise ValueError(f"Failed to read file '{filename}': {e}")

        file_payload.append(("files", (filename, file_content, "application/octet-stream"))) # TODO: consider when payload is too large (image too large)

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(endpoint, headers=headers, data=data, files=file_payload)

    if response.status_code != 200:
        raise Exception(f"Failed to upload files: {response.text}")
    
    return response.json()


@mcp.tool()
async def get_status(file_id: str, token: str) -> dict:
    """
    Retrieve the processing status of an uploaded file from the DREX API.

    Arguments:
        file_id (str): Unique identifier returned after a successful file upload.
        token (str): Authorization token for authenticating API requests.

    Returns:
        dict: Dictionary containing the current status details, such as processing state, timestamps, and any additional metadata.

    Raises:
        Exception: If the API response indicates a failure or the file ID is invalid.
    """
    endpoint = f"{DREX_BASE_URL}/files/{file_id}/status"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get file {file_id} status: {response.text}")
    return response.json()


@mcp.tool()
async def get_file_results(file_id: str, token: str) -> dict:
    """
    Retrieve the processed results of an uploaded file from the DREX API.

    Arguments:
        file_id (str): Unique identifier returned after a successful file upload and processing completion.
        token (str): Authorization token for authenticating API requests.

    Returns:
        dict: Dictionary containing the final processing results.

    Raises:
        Exception: If the results are unavailable, the processing is incomplete, or the API returns an error.
    """
    endpoint = f"{DREX_BASE_URL}/blob-data-fetch/{file_id}"
    revgrid_endpoint = f"{DREX_BASE_URL}/drexRevGrid-fetch/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, headers=headers)
        revgrid_response = await client.get(revgrid_endpoint, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to get file {file_id} object details: {response.text}")
    if revgrid_response.status_code != 200:
        raise Exception(f"Failed to get file {file_id} revision grid: {revgrid_response.text}")
    return {"file_details": response.json(), "revgrid": revgrid_response.json()}



if __name__ == "__main__":
    mcp.run(transport="stdio")
