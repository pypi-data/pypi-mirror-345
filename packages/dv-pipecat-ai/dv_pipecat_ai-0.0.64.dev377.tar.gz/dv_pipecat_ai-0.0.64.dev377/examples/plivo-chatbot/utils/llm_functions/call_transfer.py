import traceback
import urllib.parse

import aiohttp
from env_config import api_config  # Import api_config
from loguru import logger
from utils.plivo_utils import create_plivo_basic_auth_header  # Import the utility function

# Define the tool schema for the LLM
call_transfer_tool = {
    "name": "call_transfer",
    "description": "Transfers the current call to a specified PSTN number or SIP endpoint.",
    "parameters": {
        "type": "object",
        "properties": {
            "target": {
                "type": "string",
                "description": "The destination PSTN number (e.g., '+15551234567') or SIP URI (e.g., 'sip:user@example.com') to transfer the call to.",
            },
        },
        "required": ["target"],
    },
}


async def call_transfer_handler(
    fn_name: str,
    tool_call_id: str,
    args: dict,
    llm_context,
    result_callback,
    telephony_provider: str,
    call_id: str,  # Plivo CallUUID or Exotel CallSid
    bot_logger,
):
    """
    Handles the call_transfer function call from the LLM.
    """
    target = args.get("target")
    bot_logger.info(
        f"Attempting call transfer. Provider: {telephony_provider}, Call ID: {call_id}, Target: {target}"
    )

    if not target:
        error_message = "Missing required parameter: target"
        bot_logger.error(error_message)
        await result_callback({"status": "error", "message": "Target number not present."})
        return

    if telephony_provider == "plivo":
        try:
            # Use api_config for credentials and URL
            plivo_auth_id = api_config.PLIVO_AUTH_ID
            plivo_auth_token = api_config.PLIVO_AUTH_TOKEN
            ngrok_url = api_config.NGROK_URL

            if not all([plivo_auth_id, plivo_auth_token, ngrok_url]):
                error_message = "Plivo credentials or NGROK URL not configured in api_config."
                bot_logger.error(error_message)
                await result_callback(
                    {"status": "error", "message": "Unable to transfer call currently."},
                )
                return

            # Construct the aleg_url pointing to the XML endpoint
            encoded_target = urllib.parse.quote(target)
            # Using /pc/v1 prefix as established in server.py
            aleg_url = f"{ngrok_url}/pc/v1/plivo/transfer_xml?target={encoded_target}"

            # Plivo API endpoint for transferring a call
            # Note: Plivo uses CallUUID which we map to call_id here
            transfer_api_url = f"https://api.plivo.com/v1/Account/{plivo_auth_id}/Call/{call_id}/"

            payload = {
                "legs": "aleg",
                "aleg_url": aleg_url,
                "aleg_method": "GET",
            }  # Using GET for simplicity for the XML endpoint

            bot_logger.info(
                f"Calling Plivo Transfer API: {transfer_api_url} with payload: {payload}"
            )

            # Use the utility function to get headers
            headers = create_plivo_basic_auth_header(plivo_auth_id, plivo_auth_token)
            async with aiohttp.ClientSession() as session:
                # Use the generated headers
                async with session.post(
                    transfer_api_url, json=payload, headers=headers
                ) as response:
                    response_text = await response.text()
                    if 200 <= response.status < 300:
                        bot_logger.info(
                            f"Plivo transfer API call successful (Status: {response.status}). Response: {response_text}"
                        )

                        await result_callback(
                            {"status": "success", "message": "Call transfer initiated."},
                        )
                    else:
                        error_message = f"Plivo transfer API call failed (Status: {response.status}). Response: {response_text}"
                        bot_logger.error(error_message)
                        await result_callback({"status": "error", "message": error_message})

        except Exception as e:
            bot_logger.exception(e)
            await result_callback({"status": "error", "message": "Unable to transfer call."})

    elif telephony_provider == "exotel":
        # Placeholder for Exotel implementation
        message = "Call transfer for Exotel is not yet implemented."
        bot_logger.warning(message)
        await result_callback({"status": "skipped", "message": message})
        pass  # Do nothing for Exotel for now
    else:
        message = f"Call transfer not supported for telephony provider: {telephony_provider}"
        bot_logger.warning(message)
        await result_callback(
            {"status": "skipped", "message": "Call Transfer failed due to technical issues."},
        )
