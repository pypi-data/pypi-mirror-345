import uvicorn
import os
from fastapi import FastAPI, WebSocket, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, PlainTextResponse
import asyncio
import aiohttp
from urllib.parse import parse_qs
import aioboto3
import json
from botocore.exceptions import ClientError
from transcript_service import get_transcript_text, get_transcript_url
import traceback
import plivo
import urllib.parse

app = FastAPI()
ngrok_url = os.getenv("NGROK_URL")
print(ngrok_url)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

call_config_cache = {}


@app.post("/uv/call")
async def make_call(request: Request):
    try:
        call_details = await request.json()
        print(call_details)

        call_id = call_details.get("call_id")
        update_call_status_url = call_details.get("update_call_status_url")
        call_config = call_details.get("call_config")

        # from_phone_number = call_details.get("from")
        # to_phone_number = call_details.get("recipient_phone_number")

        # Prepare the request body for Ultravox
        call_request_body = {
            "firstSpeaker": "FIRST_SPEAKER_AGENT",  # or "FIRST_SPEAKER_USER" based on your needs
            "systemPrompt": call_config.get(
                "prompt", "You are a helpful assistant."
            ),  # from call_config
            "voice": call_config.get("voice", "Mark"),  # or any default voice
            "languageHint": call_config.get("language", "en"),
            "medium": {"plivo": {}},
            "maxDuration": call_config.get("max_duration", "180s"),
            "inactivityMessages": [
                {"duration": "6s", "message": "Are you still there?"},
                {
                    "duration": "10s",
                    "message": "If there's nothing else, may I end the call?",
                    "endBehavior": "END_BEHAVIOR_HANG_UP_SOFT",
                },
                # {
                #     "duration": "10s",
                #     "message": "Thank you for calling. Have a great day. Goodbye.",
                #     "endBehavior": "END_BEHAVIOR_HANG_UP_SOFT",
                # },
            ],
            # Include other parameters as needed
            # "selectedTools": [],  # If you are using tools
            # "maxDuration": "3600s",  # For example
            # "recordingEnabled": True,
        }

        # If you have initialMessages or other parameters, include them
        # For example, if you have an intro message
        # if call_config.get("intro_message"):
        #     call_request_body["initialMessages"] = [
        #         {
        #             "speaker": "SPEAKER_AGENT",
        #             "message": call_config.get("intro_message"),
        #         }
        #     ]

        # Use your Ultravox API key
        ultravox_api_key = os.getenv("ULTRAVOX_API_KEY")
        headers = {
            "X-API-Key": f"{ultravox_api_key}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.ultravox.ai/api/calls", headers=headers, json=call_request_body
            ) as response:
                if response.status == 201:
                    resp_json = await response.json()
                    # Extract callId from the response
                    ultravox_call_id = resp_json.get("callId")
                    call_config["ultravox_call_id"] = ultravox_call_id
                    join_url = resp_json.get("joinUrl")
                    # Return success
                else:
                    resp_text = await response.text()
                    print(f"Failed to create call: {response.status} {resp_text}")
                    raise HTTPException(status_code=500, detail="Failed to create call")
        plivo_client = plivo.RestClient(os.getenv("PLIVO_AUTH_ID"), os.getenv("PLIVO_AUTH_TOKEN"))
        update_call_status_url = call_details.get("update_call_status_url")
        call_id = call_details.get("call_id")

        encoded_join_url = urllib.parse.quote(join_url)
        if update_call_status_url:
            encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)
            encoded_call_id = urllib.parse.quote(call_id)
            call_config_cache[call_id] = call_config
            answer_url = f"{ngrok_url}/uv/start_call?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}&join_url={encoded_join_url}"
            hangup_url = f"{ngrok_url}/uv/plivo_hangup_callback?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
            ring_url = f"{ngrok_url}/uv/ring_call?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
        else:
            answer_url = f"{ngrok_url}/uv/start_call?join_url={encoded_join_url}"
            hangup_url = f"{ngrok_url}/uv/plivo_hangup_callback"
            ring_url = f"{ngrok_url}/uv/ring_call"

        plivo_client.calls.create(
            from_=call_details.get("from"),
            to_=call_details.get("recipient_phone_number"),
            answer_url=answer_url,
            hangup_url=hangup_url,
            ring_url=ring_url,
            answer_method="POST",
        )
    except HTTPException as e:
        print(f"Exception occurred in make_call: {e}")
        traceback.print_exc()
        raise e  # Re-raise the HTTPException to send the same status code and message
    except Exception as e:
        print(f"Exception occurred in make_call: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/uv/start_call")
async def start_call(
    request: Request,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None),
    join_url: str = Query(None),
):
    request_body = await request.body()
    # print(f"Request body: {request_body}")
    """
    Request body: b'ALegRequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&ALegUUID=38cb006a-e25d-4455-9862-27550dbea7e9&BillRate=0.005&CallStatus=in-progress&CallUUID=38cb006a-e25d-4455-9862-27550dbea7e9&CountryCode=IN&Direction=outbound&Event=StartApp&From=918035735900&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&RouteType=Domestic_Anchored&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-10-25+14%3A13%3A37.779297&To=919494865411'
    """
    formated_xml = open("templates/uv-stream.xml").read().format(ultravox_join_url=join_url)
    print("formated_xml:", formated_xml)
    return HTMLResponse(formated_xml, media_type="application/xml")


@app.post("/uv/ring_call")
async def ring_call(
    request: Request, update_call_status_url: str = Query(None), callback_call_id: str = Query(None)
):
    request_body = await request.body()
    print(f"Request body: {request_body}")
    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]
    print(f"Ringing: Call UUID: {call_uuid}")
    """
    Request body: b'CallStatus=ringing&CallUUID=38cb006a-e25d-4455-9862-27550dbea7e9&CallerName=&Direction=outbound&Event=Ring&From=%2B918035735900&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&SessionStart=2024-10-25+14%3A13%3A35.846244&To=919494865411'
    """
    try:
        if update_call_status_url:
            # Parse the request body to extract CallUUID
            parsed_body = parse_qs(request_body.decode())
            call_uuid = parsed_body.get("CallUUID", [None])[0]
            print(f"Update call status URL: {update_call_status_url}")
            url = update_call_status_url.format(callback_call_id)
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    url,
                    json={
                        "call_id": callback_call_id,
                        "status": "ringing",
                        "call_provider": "plivo",
                        "call_provider_call_id": call_uuid,
                    },
                ) as response:
                    response_text = await response.text()
                    print(
                        f"Ringing callback Response status: {response.status}, Response body: {response_text}"
                    )
    except Exception as e:
        print("Exception occurred in updating status call back in ring_call")
        traceback.print_exc()
    return PlainTextResponse("", status_code=200)


@app.post("/uv/plivo_hangup_callback")
async def plivo_hangup_callback(
    request: Request, update_call_status_url: str = Query(None), callback_call_id: str = Query(None)
):
    """
    Sample request.body()
    Request body: b'ALegRequestUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&ALegUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&AnswerTime=2024-09-26+14%3A05%3A18&BillDuration=120&BillRate=0.005&CallStatus=completed&CallUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&Direction=outbound&Duration=66&EndTime=2024-09-26+14%3A06%3A23&Event=Hangup&From=917658035735900&HangupCause=NORMAL_CLEARING&HangupCauseCode=4000&HangupCauseName=Normal+Hangup&HangupSource=Callee&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-09-26+08%3A35%3A10.910772&StartTime=2024-09-26+14%3A05%3A08&To=91773345553974342&TotalCost=0.01000'
    """
    # add any post call hangup processing
    request_body = await request.body()
    print(f"Request body: {request_body}")
    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]
    try:
        if update_call_status_url:
            url = update_call_status_url.format(callback_call_id)
            call_status = parsed_body.get("CallStatus", [None])[0]
            call_sub_status = parsed_body.get("HangupCauseName", [None])[0]
            if call_sub_status and "XML" in call_sub_status:
                call_sub_status = "Normal Hangup"
            if callback_call_id in call_config_cache:
                del call_config_cache[callback_call_id]
            # Get transcript from S3
            print(
                f"Status update payload: url {url}; callback_call_id {callback_call_id}, {call_status}, {call_uuid}"
            )
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    url,
                    json={
                        "call_id": callback_call_id,
                        "status": call_status,
                        "sub_status": call_sub_status,
                        "call_provider": "plivo",
                        "call_provider_call_id": call_uuid,
                    },
                ) as response:
                    print("Got response for plivo_hangup_callback to backend")
                    response_text = await response.text()
                    print(
                        f"Hangup callback Response status: {response.status}, Response body: {response_text}"
                    )
    except Exception as e:
        print("Error in hangup callback", flush=True)
        traceback.print_exc()
    return PlainTextResponse("", status_code=200)


@app.get("/transcript/{call_id}")
async def get_call_transcript(call_id: str):
    try:
        transcript = await get_transcript_text(call_id)
        if transcript:
            return {"status": "success", "transcript": transcript}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/transcript_url/{call_id}")
async def get_call_transcript_url(call_id: str):
    try:
        transcript_url = get_transcript_url(call_id)
        if transcript_url:
            return {"status": "success", "transcript": transcript_url}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    environment = os.getenv("ENVIRONMENT", "production")
    reload = environment == "development"
    print("Environment: ", environment)
    # Make sure to not add more than 1 workers and the call_config_cache will start breaking. So, use redis instead of local in that case.
    uvicorn.run("ultravox-server:app", host="0.0.0.0", port=8765, reload=reload)
