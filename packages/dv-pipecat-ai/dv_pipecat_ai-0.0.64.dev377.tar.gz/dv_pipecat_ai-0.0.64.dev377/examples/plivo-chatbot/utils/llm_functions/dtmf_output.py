import traceback

import aiohttp
from env_config import api_config
from utils.plivo_utils import create_plivo_basic_auth_header

# Define the tool schema for the LLM
dtmf_output_tool = {
    "name": "dtmf_output",
    "description": "Sends DTMF tones (digits 0-9, *, #) during the current call. Useful for interacting with IVR systems or entering codes.",
    "parameters": {
        "type": "object",
        "properties": {
            "digits": {
                "type": "string",
                "description": "The sequence of DTMF digits to send (e.g., '123#'). Allowed characters: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, *, #.",
            },
        },
        "required": ["digits"],
    },
}


async def dtmf_output_handler(
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
    Handles the dtmf_output function call from the LLM.
    """
    digits = args.get("digits")
    bot_logger.info(
        f"Attempting to send DTMF. Provider: {telephony_provider}, Call ID: {call_id}, Digits: {digits}"
    )

    if not digits:
        error_message = "Missing required parameter: digits"
        bot_logger.error(error_message)
        # Use a more generic message for the callback
        await result_callback({"status": "error", "message": "DTMF digits not provided."})
        return

    # Basic validation for allowed DTMF characters (optional but recommended)
    allowed_chars = set("0123456789*#")
    if not set(digits).issubset(allowed_chars):
        error_message = (
            f"Invalid characters in digits parameter: {digits}. Only 0-9, *, # are allowed."
        )
        bot_logger.error(error_message)
        # Use a more generic message for the callback
        await result_callback({"status": "error", "message": "Invalid DTMF digits provided."})
        return

    if telephony_provider == "plivo":
        try:
            # Check both auth_id and auth_token like in call_transfer
            plivo_auth_id = api_config.PLIVO_AUTH_ID
            plivo_auth_token = api_config.PLIVO_AUTH_TOKEN
            # Check both credentials
            if not all([plivo_auth_id, plivo_auth_token]):
                error_message = "Plivo credentials not configured in api_config."
                bot_logger.error(error_message)
                # Use generic callback message like in call_transfer
                await result_callback(
                    {"status": "error", "message": "DTMF failed due to configuration issue."},
                )
                return

            # Plivo API endpoint for sending DTMF
            dtmf_api_url = f"https://api.plivo.com/v1/Account/{plivo_auth_id}/Call/{call_id}/DTMF/"

            payload = {"digits": digits}

            # Get headers using the utility function, passing credentials explicitly
            headers = create_plivo_basic_auth_header(plivo_auth_id, plivo_auth_token)
            # Check if headers were successfully created (utility returns {} on failure)
            if not headers:
                error_message = "Failed to create Plivo auth headers (check credentials)."
                bot_logger.error(error_message)
                # Use a more generic message for the callback
                await result_callback(
                    {"status": "error", "message": "DTMF failed due to configuration issue."},
                )
                return

            bot_logger.info(f"Calling Plivo DTMF API: {dtmf_api_url} with payload: {payload}")

            async with aiohttp.ClientSession() as session:
                async with session.post(dtmf_api_url, json=payload, headers=headers) as response:
                    response_text = await response.text()
                    # Plivo Send Digits API returns 202 Accepted on success
                    if response.status == 202:
                        bot_logger.info(
                            f"Plivo DTMF API call successful (Status: {response.status}). Response: {response_text}"
                        )
                        await result_callback(
                            {"status": "success", "message": "DTMF digits sent."},
                        )
                    else:
                        error_message = f"Plivo DTMF API call failed (Status: {response.status}). Response: {response_text}"
                        bot_logger.error(error_message)
                        await result_callback(
                            # Keep specific error message here for Plivo API failure
                            {"status": "error", "message": error_message},
                        )

        except Exception as e:
            # Use logger.exception for automatic traceback logging
            bot_logger.exception(f"Error sending Plivo DTMF: {e}")
            # Use a more generic message for the callback
            await result_callback({"status": "error", "message": "Unable to send DTMF tones."})

    elif telephony_provider == "exotel":
        # Placeholder for Exotel implementation
        message = "DTMF output for Exotel is not yet implemented."
        bot_logger.warning(message)
        await result_callback({"status": "skipped", "message": message})
        pass
    else:
        message = f"DTMF output not supported for telephony provider: {telephony_provider}"
        bot_logger.warning(message)
        # Use a more generic message for the callback
        await result_callback(
            {"status": "skipped", "message": "DTMF failed due to technical issues."}
        )
