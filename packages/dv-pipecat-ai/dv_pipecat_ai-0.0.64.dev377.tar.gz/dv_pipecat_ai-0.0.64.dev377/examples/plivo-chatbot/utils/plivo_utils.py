import base64

from env_config import api_config
from loguru import logger


def create_plivo_basic_auth_header(auth_id: str = None, auth_token: str = None) -> dict:
    """
    Creates the Basic Authentication header required for Plivo API calls.

    Args:
        auth_id: Plivo Auth ID. Defaults to api_config.PLIVO_AUTH_ID.
        auth_token: Plivo Auth Token. Defaults to api_config.PLIVO_AUTH_TOKEN.

    Returns:
        A dictionary containing the 'Authorization' and 'Content-Type' headers.

    Raises:
        ValueError: If auth_id or auth_token is missing.
    """
    auth_id = auth_id or api_config.PLIVO_AUTH_ID
    auth_token = auth_token or api_config.PLIVO_AUTH_TOKEN

    if not auth_id or not auth_token:
        logger.error("Plivo Auth ID or Auth Token is missing.")
        raise ValueError("Plivo Auth ID or Auth Token is missing.")

    auth_string = f"{auth_id}:{auth_token}"
    auth_bytes = auth_string.encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode("ascii")

    headers = {
        "Authorization": f"Basic {base64_auth}",
        "Content-Type": "application/json",
    }
    return headers
