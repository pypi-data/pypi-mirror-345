import aiohttp
from env_config import api_config
from fastapi import HTTPException


async def update_webcall_status(call_id, callback_call_id, status, sub_status, logger):
    async with aiohttp.ClientSession() as session:
        call_request_body = {
            "call_id": call_id,
            "status": status,
            "call_provider": "livekit",
            "sub_status": sub_status,
        }
        request_headers = {
            "Content-Type": "application/json",
        }
        async with session.patch(
            f"{api_config.CALLING_BACKEND_URL}/calling/webcall/status",
            headers=request_headers,
            json=call_request_body,
        ) as response:
            if response.status == 200:
                logger.info(
                    "status updated successfully for webcall with call_id",
                    call_id=callback_call_id,
                )
                # Return success
            else:
                raise HTTPException(status_code=500, detail="Failed to update webcall status")
