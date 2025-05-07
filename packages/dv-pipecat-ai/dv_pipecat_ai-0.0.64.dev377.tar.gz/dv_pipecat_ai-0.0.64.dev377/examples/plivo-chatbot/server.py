import asyncio
import json
import os
import re  # Import re for regex matching
import time  # Import time for sleep
import traceback
import urllib.parse
from contextlib import asynccontextmanager
from typing import Optional
from urllib.parse import parse_qs

import aioboto3
import aiohttp
import plivo
import redis.asyncio as redis
import uvicorn
from bot import run_bot
from botocore.exceptions import ClientError
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# IMPORTANT: This logger_config import must come first, before any other imports that might use loguru
from pipecat.utils import logger_config
from rag.weaviate_client import weaviate_client_manager
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse
from starlette.status import HTTP_503_SERVICE_UNAVAILABLE  # Import status code
from utils.generic_functions.common import call_config_validator
from utils.transcript import get_transcript_text, get_transcript_url
from utils.tts import (
    get_tts_file_from_redis,  # Import the new function
    put_file_on_redis,
)
from webcall_bot import run_webcall_bot

# Add after the existing imports
session = aioboto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

REDIS_URL = os.getenv("REDIS_URL")
redis_pool = None
redis_client = None
is_shutting_down = False
DOCKER_KILL_TIMEOUT = 240


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize connection
    global redis_pool, redis_client, is_shutting_down

    # Initialize connections
    # Set decode_responses=False to handle binary data like cached MP3s correctly
    redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=False)
    redis_client = redis.Redis.from_pool(redis_pool)
    logger.info("Redis connection pool initialized (decode_responses=False)")
    is_shutting_down = False
    yield
    is_shutting_down = True
    logger.info("Application is shutting down, waiting for active calls to complete...")
    # Wait for active websocket connections to finish (with timeout)
    if websocket_connections:
        logger.info(f"Waiting for {len(websocket_connections)} active connections to complete...")
        timeout = DOCKER_KILL_TIMEOUT - 30  # seconds (less than Docker's stop timeout)
        start_time = time.time()

        while websocket_connections and (time.time() - start_time < timeout):
            active_calls = ", ".join(websocket_connections.keys())
            logger.info(
                f"Still waiting for {len(websocket_connections)} connections: {active_calls}"
            )
            await asyncio.sleep(10)
    # Clean up resources
    if redis_client:
        await redis_client.aclose()
    logger.info("Graceful shutdown completed")
    # Wait for active websocket connections to finish (with timeout)


app = FastAPI(lifespan=lifespan)
router = APIRouter()

ngrok_url = os.getenv("NGROK_URL")
print("ngrok_url:", ngrok_url)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

websocket_connections = {}
redis_prefix = "pc_"


@router.get("/data")
def handle_schema():
    from rag.helpers import agent

    return agent("prahlad से इंस्टामार्ट के नजदीकी जोन कौन से हैं?")

    import weaviate.classes as wvc

    # FOR sheet
    # query = "which is the best zone for me?"
    # field_descriptions = """
    # **Field Information:**
    # - City: Where deliveries occur (e.g., Ahmedabad)
    # - Zone: Specific delivery area within city (e.g., Prahlad Nagar)
    # - Fleet: Service type (Instamart/Food)
    # - day21_orders: Orders needed to qualify for bonus
    # - day21_bonus: Bonus amount for completing 21-day orders
    # - total_bonus: Bonus amount that the user will receive
    # - bag_price: Upfront equipment cost
    # - nearest_zone: Nearby alternative zones
    # - nearest_zone_bonus: Bonus amounts in nearby zones
    # """

    # formatting_instructions = f"""
    # DIRECTIVES:
    # 1. Report exact bonus numbers from day21_bonus/total_bonus if available
    # 2. Compare with nearest_zone_bonus when higher
    # 3. Only say 'no info' if ALL bonus fields = 0 \n
    # '{query}'

    # {field_descriptions}
    # """

    # # FOR faq
    # # query = "How can i maximize my earnings?"
    # # formatting_instructions = f"Keep the answer short and concise to the query - {query}"
    # return weaviate_client.collections.get(collection_name2).generate.near_text(query=query, limit=10, grouped_task=formatting_instructions, )


def get_redis_key(call_id: str) -> str:
    """Generates a prefixed Redis key for a given call ID."""
    return f"{redis_prefix}{call_id}"


async def get_call_config(call_id: str):
    """Gets call config from Redis. Decodes bytes to string before JSON parsing."""
    call_config_bytes = await redis_client.get(get_redis_key(call_id))
    call_config = json.loads(call_config_bytes.decode("utf-8")) if call_config_bytes else None
    return call_config


async def set_call_config(call_id: str, call_config):
    """Sets call config in Redis. Encodes JSON string to bytes."""
    await redis_client.setex(
        get_redis_key(call_id), 48 * 60 * 60, json.dumps(call_config).encode("utf-8")
    )


async def delete_call_config(call_id: str):
    """Deletes call config from  Redis."""
    try:
        redis_key = get_redis_key(call_id)
        if await redis_client.exists(redis_key):
            await redis_client.delete(redis_key)
    except Exception as e:
        logger.error(f"Error deleting call config for call_id {call_id}: {e}", call_id=call_id)


@router.post("/inbound_plivo_hangup")
async def inbound_plivo_hangup_callback(request: Request):
    try:
        request_body = await request.body()
        body_str = request_body.decode("utf-8")
        parsed_params = parse_qs(body_str)
        call_sid = parsed_params.get("CallUUID", [None])[0]
        url = f"{os.getenv('CALLING_BACKEND_URL')}/calling/inbound/status"

        call_status = parsed_params.get("CallStatus", [None])[0]
        call_sub_status = parsed_params.get("HangupCauseName", [None])[0]
        if call_sub_status and "XML" in call_sub_status:
            call_sub_status = "Normal Hangup"

        # Delete call config using helper function
        await delete_call_config(call_sid)
        transcript = get_transcript_url(call_sid)
        logger.info(
            f"Status update payload: url {url}; callback_call_id {call_sid}, {call_status}",
            call_id=call_sid,
        )
        async with aiohttp.ClientSession() as session:
            async with session.patch(
                url,
                json={
                    "call_sid": call_sid,
                    "status": call_status,
                    "sub_status": call_sub_status,
                    "call_provider": "plivo",
                    "transcript": transcript,
                },
            ) as response:
                logger.info("Got response for plivo_hangup_callback to backend", call_id=call_sid)
                if response.status == 200:
                    response_json = await response.json()
                    res_message = response_json.get("message", "no message found")
                else:
                    response_text = await response.text()
                    res_message = f"{response_text}"
                res_message = res_message.replace("{", "").replace("}", "")
                logger.info(
                    f"Hangup callback Response status: {response.status}, Response body {res_message}",
                    call_id=call_sid,
                )
    except HTTPException as e:
        logger.error(
            f"HTTPException occurred in inbound_plivo_hangup_callback: {e}", call_id=call_sid
        )
        raise e  # Re-raise the HTTPException to send the same status code and message
    except Exception as e:
        logger.error(f"Exception occurred in inbound_plivo_hangup_callback: {e}", call_id=call_sid)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/inbound_call")
async def make_plivo_inbound_call(request: Request):
    try:
        request_body = await request.body()
        body_str = request_body.decode("utf-8")
        parsed_params = parse_qs(body_str)
        from_number = parsed_params.get("From", [None])[0]
        to_number = parsed_params.get("To", [None])[0]
        call_sid = parsed_params.get("CallUUID", [None])[0]
        client = parsed_params.get("client", [None])[0]

        if client == "practo":
            url = f"{os.getenv('CALLING_BACKEND_URL')}/calling/inbound?client=practo"
        else:
            url = f"{os.getenv('CALLING_BACKEND_URL')}/calling/inbound"

        logger.info(
            f"Data received: from_number={from_number}, to_number={to_number}, call_sid={call_sid}",
            call_id=call_sid,
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"from_number": from_number, "to_number": to_number, "call_sid": call_sid},
            ) as response:
                response.raise_for_status()
                call_details = await response.json()
                logger.info(
                    "Ringing callback Response status: {}, Response body: {}",
                    response.status,
                    call_details,
                    call_id=call_sid,
                )

        call_config_validator(call_details.get("call_config"))
        max_call_length = call_details.get("call_config").get("max_call_length", 240)
        encoded_call_sid = urllib.parse.quote(call_sid)

        # Using call_sid instead of call_id because the hangup url doesn't send call_id
        await set_call_config(call_sid, call_details.get("call_config"))

        # Add /pc prefix to the WebSocket URL path
        # Construct the WebSocket URL with the new prefix
        wss_ngrok_url = ngrok_url.replace("https:", "wss:") + "/pc/v1/ws"
        if not max_call_length:
            # Note this case would arise only if the user passes 0 in the  max_call_length in the call_config.
            max_call_length = 240

        wss_ngrok_url += f"?callback_call_id={encoded_call_sid}"

        logger.info(f"Encoded wss_ngrok_url: {wss_ngrok_url}", call_id=call_sid)

        # Get record setting from call_config
        record_locally = call_details.get("call_config", {}).get("record", False)

        # If recording locally, disable Plivo's recording
        record_session = "false" if record_locally else "true"

        with open("templates/streams.xml") as f:
            formated_xml = f.read().format(
                ngrok_url=wss_ngrok_url,
                max_call_length=max_call_length,
                record_session=record_session,
            )

        # get_call_config_url.format(callback_call_id)
        return HTMLResponse(formated_xml, media_type="application/xml")

    except HTTPException as e:
        logger.exception(f"HTTPException occurred in make_inbound_call", call_id=call_sid)
        logger.exception(traceback.format_exc(), call_id=call_sid)
        raise e  # Re-raise the HTTPException to send the same status code and message
    except Exception as e:
        logger.exception(f"Exception occurred in make_inbound_call", call_id=call_sid)
        logger.exception(traceback.format_exc(), call_id=call_sid)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/call")
async def make_call(request: Request):
    try:
        call_details = await request.json()
        print(f"make_call request body:{call_details}")
        call_id = call_details.get("call_id")
        # logger.info(f"make_call request body:{call_details}", call_id=call_id)
        call_config_validator(call_details.get("call_config"))
        plivo_client = plivo.RestClient(os.getenv("PLIVO_AUTH_ID"), os.getenv("PLIVO_AUTH_TOKEN"))
        update_call_status_url = call_details.get("update_call_status_url")
        max_call_length = call_details.get("call_config").get("max_call_length", 240)
        encoded_call_id = urllib.parse.quote(call_id)
        record = call_details.get("call_config", {}).get("record", False)
        # Add /pc prefix to callback URLs
        if update_call_status_url:
            encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)
            await set_call_config(call_id, call_details.get("call_config"))
            # Construct callback URLs with the new prefix
            answer_url = f"{ngrok_url}/pc/v1/start_call?callback_call_id={encoded_call_id}&max_call_length={max_call_length}&record={record}"
            hangup_url = f"{ngrok_url}/pc/v1/plivo_hangup_callback?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
            ring_url = f"{ngrok_url}/pc/v1/ring_call?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}"
        else:
            await set_call_config(call_id, call_details.get("call_config"))
            answer_url = (
                # Construct callback URLs with the new prefix
                f"{ngrok_url}/pc/v1/start_call?callback_call_id={encoded_call_id}&record={record}"
            )
            hangup_url = (
                f"{ngrok_url}/pc/v1/plivo_hangup_callback?callback_call_id={encoded_call_id}"
            )
            ring_url = f"{ngrok_url}/pc/v1/ring_call?callback_call_id={encoded_call_id}"

        plivo_client.calls.create(
            from_=call_details.get("from"),
            to_=call_details.get("recipient_phone_number"),
            answer_url=answer_url,
            hangup_url=hangup_url,
            ring_url=ring_url,
            answer_method="POST",
        )
        # logger.info(f"Plivo call initiated to {call_details.get('recipient_phone_number')}", call_id=call_id)
        # plivo_client.calls.create(
        #     from_=call_details.get("from"),
        #     to_=call_details.get("recipient_phone_number"),
        #     answer_url=f"{ngrok_url}/start_call",
        #     hangup_url=f"{ngrok_url}/plivo_hangup_callback",
        #     answer_method="POST",
        # )
    except HTTPException as e:
        logger.error(f"HTTPException occurred in make_call: {e}", call_id=call_id)
        raise e  # Re-raise the HTTPException to send the same status code and message
    except Exception as e:
        logger.error(f"Exception occurred in make_call: {e}", call_id=call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/start_call")
async def start_call(
    request: Request,
):
    request_body = await request.body()

    query_params = dict(request.query_params)
    callback_call_id: str = query_params.get("callback_call_id", None)
    max_call_length: int = query_params.get("max_call_length", None)
    """
    Request body: b'ALegRequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&ALegUUID=38cb006a-e25d-4455-9862-27550dbea7e9&BillRate=0.005&CallStatus=in-progress&CallUUID=38cb006a-e25d-4455-9862-27550dbea7e9&CountryCode=IN&Direction=outbound&Event=StartApp&From=918035735900&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&RouteType=Domestic_Anchored&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-10-25+14%3A13%3A37.779297&To=919494865411'
    """
    # Add /pc prefix to the WebSocket URL path
    # Construct the WebSocket URL with the new prefix
    wss_ngrok_url = ngrok_url.replace("https:", "wss:") + "/pc/v1/ws"
    if not max_call_length:
        # Note this case would arise only if the user passes 0 in the  max_call_length in the call_config.
        max_call_length = 240

    encoded_call_id = urllib.parse.quote(callback_call_id)
    wss_ngrok_url += f"?callback_call_id={encoded_call_id}"
    logger.info(f"encoded wss_ngrok_url: {wss_ngrok_url}", call_id=callback_call_id)

    # Get record setting from query params
    record_locally = query_params.get("record", "False").lower() == "true"

    # If recording locally, disable Plivo's recording
    record_session = "false" if record_locally else "true"

    with open("templates/streams.xml") as f:
        template_content = f.read()

    if record_session == "false":
        # Use regex to remove the entire Record element regardless of its content

        # This will match <Record ...any content... />

        template_content = re.sub(r"\s*<Record.*?/>\s*", "\n    ", template_content)

    formatted_xml = template_content.format(
        ngrok_url=wss_ngrok_url, max_call_length=max_call_length, record_session=record_session
    )
    print(f"{formatted_xml}")
    # get_call_config_url.format(callback_call_id)
    return HTMLResponse(formatted_xml, media_type="application/xml")


@router.post("/ring_call")
async def ring_call(request: Request):
    request_body = await request.body()
    update_call_status_url: str = request.query_params.get("update_call_status_url", None)
    callback_call_id: str = request.query_params.get("callback_call_id", None)
    logger.info(f"Ring Request body: {request_body}", call_id=callback_call_id)
    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]
    logger.info(f"Ringing: Call UUID: {call_uuid}", call_id=callback_call_id)
    """
    Request body: b'CallStatus=ringing&CallUUID=38cb006a-e25d-4455-9862-27550dbea7e9&CallerName=&Direction=outbound&Event=Ring&From=%2B918035735900&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=38cb006a-e25d-4455-9862-27550dbea7e9&SessionStart=2024-10-25+14%3A13%3A35.846244&To=919494865411'
    """
    try:
        if update_call_status_url:
            # Parse the request body to extract CallUUID
            parsed_body = parse_qs(request_body.decode())
            call_uuid = parsed_body.get("CallUUID", [None])[0]
            logger.info(
                f"Update call status URL: {update_call_status_url}", call_id=callback_call_id
            )
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
                    if response.status == 200:
                        response_json = await response.json()
                        res_message = response_json.get("message", "no message found")
                    else:
                        response_text = await response.text()
                        res_message = f"{response_text}"
                    res_message = res_message.replace("{", "").replace("}", "")
                    logger.info(
                        f"Ringing callback Response status: {response.status}, Response body: {res_message}",
                        call_id=callback_call_id,
                    )
    except Exception as e:
        logger.error(
            "Exception occurred in updating status call back in ring_call", call_id=callback_call_id
        )
    return PlainTextResponse("", status_code=200)


@router.get("/plivo/transfer_xml")
async def plivo_transfer_xml(target: str = Query(...)):
    """Generates Plivo XML to dial a number or SIP endpoint for call transfer."""
    logger.info(f"Generating transfer XML for target: {target}")
    # Basic check for SIP URI format (adjust regex as needed)
    if re.match(r"^sip:.*@.*", target):
        xml_content = f"""
<Response>
    <Dial>
        <Sip>{target}</Sip>
    </Dial>
</Response>
"""
    else:
        # Assume it's a PSTN number
        xml_content = f"""
<Response>
    <Dial>
        <Number>{target}</Number>
    </Dial>
</Response>
"""
    logger.debug(f"Generated XML: {xml_content}")
    return HTMLResponse(xml_content.strip(), media_type="application/xml")


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None),
):
    await websocket.accept()
    logger.info("WebSocket connection accepted", call_id=callback_call_id)
    try:
        if callback_call_id:
            websocket_connections[callback_call_id] = websocket

        # Wait for the initial connection message
        start_event = await websocket.receive_json()
        logger.info("Start event received:", start_event, flush=True, call_id=callback_call_id)
        if start_event.get("event") != "start":
            raise ValueError("Expected 'start' event not received")

        # Extract the stream ID from the connection data
        stream_id = start_event.get("start").get("streamId")
        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        logger.info(f"Stream ID: {stream_id}", call_id=callback_call_id)

        call_id = start_event.get("start").get("callId")
        logger.info("call_id is here", callback_call_id, call_id=callback_call_id)
        if not call_id:
            raise ValueError("Call ID not found in connection data")

        call_config = await get_call_config(callback_call_id)

        # Run the bot with the established WebSocket connection and stream ID
        await run_bot(
            websocket, call_id, stream_id, callback_call_id, call_config, redis_client
        )  # Pass redis_client

    except Exception as e:
        logger.error(traceback.print_exc(), call_id=callback_call_id)
        logger.error(
            f"Error in WebSocket connection: {str(e)}", flush=True, call_id=callback_call_id
        )
        await websocket.close()
    finally:
        # Ensure the WebSocket is removed from the dictionary when closed
        if callback_call_id and callback_call_id in websocket_connections:
            del websocket_connections[callback_call_id]
            logger.info(
                f"Removed connection {callback_call_id} from tracking.", call_id=callback_call_id
            )


@router.post("/webcall")
async def webcall_endpoint(request: Request):
    try:
        call_details = await request.json()
        print(f"make_call request body:{call_details}")
        call_config_validator(call_details.get("call_config"))
        update_call_status_url = call_details.get("update_call_status_url")
        call_id = call_details.get("call_id")
        call_config = call_details.get("call_config")
        await set_call_config(call_id, call_config)
        asyncio.create_task(run_webcall_bot(call_id, call_config, update_call_status_url))
        print("Process started")
        return {"message": "call started successfully"}
    except Exception as e:
        print(traceback.print_exc())
        print(f"Error in WebSocket connection: {str(e)}", flush=True)
    finally:
        logger.info("ok", call_id=call_id)


@router.post("/plivo_hangup_callback")
async def plivo_hangup_callback(
    request: Request, update_call_status_url: str = Query(None), callback_call_id: str = Query(None)
):
    """Sample request.body()
    Request body: b'ALegRequestUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&ALegUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&AnswerTime=2024-09-26+14%3A05%3A18&BillDuration=120&BillRate=0.005&CallStatus=completed&CallUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&Direction=outbound&Duration=66&EndTime=2024-09-26+14%3A06%3A23&Event=Hangup&From=917658035735900&HangupCause=NORMAL_CLEARING&HangupCauseCode=4000&HangupCauseName=Normal+Hangup&HangupSource=Callee&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=64d3290a-87a6-46b4-a6e2-20f5f4e07a02&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-09-26+08%3A35%3A10.910772&StartTime=2024-09-26+14%3A05%3A08&To=91773345553974342&TotalCost=0.01000'
    """
    # add any post call hangup processing
    request_body = await request.body()
    logger.info(
        f"Plivo hangup callback request body for call_id: {callback_call_id} is {request_body}",
        call_id=callback_call_id,
    )
    parsed_body = parse_qs(request_body.decode())
    call_uuid = parsed_body.get("CallUUID", [None])[0]
    try:
        if update_call_status_url:
            url = update_call_status_url.format(callback_call_id)
            call_status = parsed_body.get("CallStatus", [None])[0]
            call_sub_status = parsed_body.get("HangupCauseName", [None])[0]
            if call_sub_status and "XML" in call_sub_status:
                call_sub_status = "Normal Hangup"

            # Delete call config using helper function
            await delete_call_config(callback_call_id)
            transcript = get_transcript_url(callback_call_id)
            logger.info(
                f"Status update payload: url {url}; callback_call_id {callback_call_id}, {call_status}, {call_uuid}",
                call_id=callback_call_id,
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
                        "transcript": transcript,
                    },
                ) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        res_message = response_json.get("message", "no message found")
                    else:
                        response_text = await response.text()
                        res_message = f"{response_text}"

                    # Remove curly braces from the message
                    res_message = res_message.replace("{", "").replace("}", "")

                    logger.info(
                        f"Hangup callback Response status: {response.status}, Response body {res_message}",
                        call_id=callback_call_id,
                    )

    except Exception as e:
        logger.error("Error in hangup callback", flush=True, call_id=callback_call_id)
        traceback.print_exc()
    try:
        if callback_call_id:
            websocket = websocket_connections.get(callback_call_id)
            if websocket:
                await websocket.close()
                logger.info(
                    f"WebSocket connection closed for callback_call_id: {callback_call_id}",
                    call_id=callback_call_id,
                )
                del websocket_connections[callback_call_id]
    except Exception as e:
        logger.error("Websocket might be already closed", call_id=callback_call_id)

    return PlainTextResponse("", status_code=200)
    """
    User cut the call: b'AnswerTime=&BillDuration=0&BillRate=0.005&CallStatus=busy&CallUUID=672b0b3f-e4b9-46e7-8fa9-3b48c7da8683&Direction=outbound&Duration=0&EndTime=2024-10-22+16%3A41%3A21&Event=Hangup&From=%2B918035735900&HangupCause=USER_BUSY&HangupCauseCode=3010&HangupCauseName=Busy+Line&HangupSource=Carrier&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=672b0b3f-e4b9-46e7-8fa9-3b48c7da8683&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-10-22+11%3A10%3A48.129660&StartTime=2024-10-22+16%3A40%3A48&To=919494865411&TotalCost=0.00000'
    We ended the call due to timeout: b'ALegRequestUUID=cc32f844-e376-4dd7-b514-d55553f8f854&ALegUUID=cc32f844-e376-4dd7-b514-d55553f8f854&AnswerTime=2024-10-22+18%3A01%3A01&BillDuration=60&BillRate=0.005&CallStatus=completed&CallUUID=cc32f844-e376-4dd7-b514-d55553f8f854&Direction=outbound&Duration=8&EndTime=2024-10-22+18%3A01%3A09&Event=Hangup&From=918035735900&HangupCause=NORMAL_CLEARING&HangupCauseCode=4010&HangupCauseName=End+Of+XML+Instructions&HangupSource=Plivo&ParentAuthID=MAZJNLNJIYNWMZYZHIMM&RequestUUID=cc32f844-e376-4dd7-b514-d55553f8f854&STIRAttestation=Not+Applicable&STIRVerification=Not+Applicable&SessionStart=2024-10-22+12%3A30%3A58.640040&StartTime=2024-10-22+18%3A00%3A57&To=919494865411&TotalCost=0.00500'
    Call Statuses:
    in-progress
    The call was answered and is in progress. Calls with this status can be terminated using the Hangup API.

    completed
    The call was completed, terminated either by the Hangup API or by one of the parties in the call.

    ringing
    The call is ringing. This status is sent to the Ring URL.

    no-answer
    The call was not answered.

    busy
    The called line is busy.

    cancel
    The call was canceled by the caller.

    timeout
    There was a timeout while connecting your call, caused by either an issue with one of the terminating carriers or network lag in our system
    """


@router.get("/transcript/{call_id}")
async def get_call_transcript(call_id: str):
    try:
        transcript = await get_transcript_text(call_id)
        if transcript:
            return {"status": "success", "transcript": transcript}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcript_url/{call_id}")
async def get_call_transcript_url(call_id: str):
    try:
        transcript_url = get_transcript_url(call_id)
        if transcript_url:
            return {"status": "success", "transcript": transcript_url}
        else:
            raise HTTPException(status_code=404, detail="Transcript not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# This is for external clients
@router.websocket("/ext/ws")
async def external_websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection accepted")
    call_id = None  # Initialize call_id
    try:
        # Wait for the initial connection message
        start_event = await websocket.receive_json()
        call_id = start_event.get("start").get("call_sid")
        logger.info(f"Start event received: {start_event}", call_id=call_id)
        if start_event.get("event") != "start":
            raise ValueError("Expected 'start' event not received")

        # Extract the stream ID from the connection data
        stream_id = start_event.get("start").get("stream_sid")
        call_config = start_event.get("call_config")
        call_config["tts_provider"] = "elevenlabs"
        call_config["stt_provider"] = "deepgram"
        call_config["llm_model"] = "gpt-4o-mini"
        call_config["mute_during_intro"] = True
        call_config["telephony_provider"] = "custom"
        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        logger.info(f"Stream ID: {stream_id}", call_id=call_id)
        websocket_connections[call_id] = websocket
        if not call_id:
            raise ValueError("Call ID not found in connection data")

        # call_config = await get_call_config(callback_id)

        # Run the bot with the established WebSocket connection and stream ID
        await run_bot(
            websocket, call_id, stream_id, call_id, call_config, redis_client
        )  # Pass redis_client

    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", flush=True, call_id=call_id)
        await websocket.close()
    finally:
        # Ensure the WebSocket is removed from the dictionary when closed
        if call_id and call_id in websocket_connections:
            del websocket_connections[call_id]
            logger.info(f"Removed connection {call_id} from tracking.", call_id=call_id)


@router.post("/exotel/call")
async def make_exotel_call(request: Request):  # Renamed function to avoid conflict
    try:
        call_details = await request.json()
        call_id = call_details.get("call_id")
        logger.info(f"make_call: {call_details}", call_id=call_id)
        call_config_validator(call_details.get("call_config"))
        # Exotel API details
        exotel_sid = os.getenv("EXOTEL_SID")
        exotel_api_key = os.getenv("EXOTEL_API_KEY")
        exotel_api_token = os.getenv("EXOTEL_API_TOKEN")
        # Default to Singapore region
        exotel_region = os.getenv("EXOTEL_REGION", "api.exotel.com")
        app_id = os.getenv("APP_ID")
        # Construct the Exotel API URL
        exotel_api_url = f"https://{exotel_api_key}:{exotel_api_token}@{exotel_region}/v1/Accounts/{exotel_sid}/Calls/connect.json"
        exotel_flow_url = f"http://my.exotel.com/{exotel_sid}/exoml/start_voice/{app_id}"
        # Prepare the payload for the Exotel API
        # call_id = call_details.get("call_id")
        time_limit = call_details.get("call_config").get("time_limit", "180")
        encoded_call_id = urllib.parse.quote(call_id)
        update_call_status_url = call_details.get("update_call_status_url")
        encoded_update_call_status_url = urllib.parse.quote(update_call_status_url)

        payload = {
            "From": call_details.get("recipient_phone_number"),
            # Assuming you have a caller_id field
            "CallerId": call_details.get("from"),
            "Url": exotel_flow_url,  # Assuming you have a field for the Exotel flow URL
            "TimeLimit": time_limit,  # Optional
            # Add /pc prefix to callback URL
            # Construct callback URL with the new prefix
            "StatusCallback": f"{ngrok_url}/pc/v1/exotel/callback?update_call_status_url={encoded_update_call_status_url}&callback_call_id={encoded_call_id}",
            "CustomField": call_id,  # Optional
        }
        logger.info(f"Payload: {payload}", call_id=call_id)

        await set_call_config(call_id, call_details.get("call_config"))
        logger.info(f"Exotel api url {exotel_api_url}", call_id=call_id)
        # Make the API call to Exotel using aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(exotel_api_url, data=payload) as response:
                if response.status == 200:
                    response_json = await response.json()
                    logger.info(f"Exotel API response: {response_json}", call_id=call_id)
                    call_sid = response_json["Call"]["Sid"]
                    logger.info(
                        f"Exotel call initiated successfully. Call SID: {call_sid}", call_id=call_id
                    )
                    return {"status": "success", "call_sid": call_sid}
                else:
                    error_message = await response.text()
                    logger.error(f"Error initiating Exotel call: {error_message}", call_id=call_id)
                    raise HTTPException(status_code=response.status, detail=error_message)
        # )
    except HTTPException as e:
        logger.error(f"Exception occurred in make_call: {e}", call_id=call_id)
        raise e  # Re-raise the HTTPException to send the same status code and message
    except Exception as e:
        logger.error(f"Exception occurred in make_call: {e}", call_id=call_id)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.websocket("/exotel/ws")
async def exotel_websocket_endpoint(
    websocket: WebSocket,
    update_call_status_url: str = Query(None),
    callback_call_id: str = Query(None, alias="CustomField"),
):
    await websocket.accept()
    logger.info("WebSocket connection accepted", call_id=callback_call_id)
    try:
        # print("Query Parameters:")
        # print("callback_call_id:", callback_call_id)
        # query_params = websocket.query_params
        # for key, value in query_params.items():
        #     print(f"{key}: {value}")
        # if callback_call_id:
        #     websocket_connections[callback_call_id] = websocket

        # Wait for the initial connection message
        connected_event = await websocket.receive_json()
        if connected_event.get("event") != "connected":
            raise ValueError("Expected 'connected' event not received")
        start_event = await websocket.receive_json()
        logger.info(f"Start event received: {start_event}", call_id=callback_call_id)
        if start_event.get("event") != "start":
            raise ValueError("Expected 'start' event not received")
        callback_call_id = next(iter(start_event.get("start").get("custom_parameters")))
        logger.info(f"callback_call_id: {callback_call_id}", call_id=callback_call_id)
        websocket_connections[callback_call_id] = websocket

        # Extract the stream ID from the connection data
        stream_id = start_event.get("start").get("stream_sid")
        if not stream_id:
            raise ValueError("Stream ID not found in connection data")

        logger.info(f"Stream ID: {stream_id}", call_id=callback_call_id)

        call_id = start_event.get("start").get("call_sid")
        if not call_id:
            raise ValueError("Call ID not found in connection data")

        call_config = await get_call_config(callback_call_id)
        logger.info(f"Call config {call_config}", call_id=callback_call_id)
        call_config["telephony_provider"] = "exotel"

        # Run the bot with the established WebSocket connection and stream ID
        await run_bot(
            websocket, call_id, stream_id, callback_call_id, call_config, redis_client
        )  # Pass redis_client

    except Exception as e:
        logger.error(
            f"Error in WebSocket connection: {str(e)}", flush=True, call_id=callback_call_id
        )
        await websocket.close()
    finally:
        # Ensure the WebSocket is removed from the dictionary when closed
        if callback_call_id and callback_call_id in websocket_connections:
            del websocket_connections[callback_call_id]
            logger.info(
                f"Removed connection {callback_call_id} from tracking.", call_id=callback_call_id
            )


# TODO: We have optimised. So delete this. Call now directly has the websocket connection.
# @app.get("/pc/exotel/start_call") # Added /pc prefix if this were to be used
# async def start_exotel_call( # Renamed function
#     request: Request,
#     update_call_status_url: str = Query(None),
#     callback_call_id: str = Query(None, alias="CustomField"),
# ):
#     # Request body: /pc/exotel/start_call?CallSid=5979a54734e3bf7505cb8e41b96e1917&CallFrom=09494865411&CallTo=08047113155&Direction=outbound-dial&Created=Tue%2C+07+Jan+2025+15%3A51%3A06&DialWhomNumber=&HangupLatencyStartTimeExocc=&HangupLatencyStartTime=&From=09494865411&To=09513886363&CustomField=7e9095cd-b91d-4df0-945b-6b851-ss69-ex1&CurrentTime=2025-01-07+15%3A51%3A06
#     wss_ngrok_url = ngrok_url.replace("https:", "wss:") + "/pc/exotel/ws" # Added /pc prefix

#     if callback_call_id:
#         encoded_call_id = urllib.parse.quote(callback_call_id)
#         wss_ngrok_url += f"?callback_call_id={encoded_call_id}"
#     print(f"encoded wss_ngrok_url: {wss_ngrok_url}")

#     response_data = {"url": wss_ngrok_url}

#     return JSONResponse(content=response_data)


# TODO: Handle this properly.
@router.post("/exotel/callback")
async def exotel_hangup_callback(
    request: Request, update_call_status_url: str = Query(None), callback_call_id: str = Query(None)
):
    """CallSid - an alpha-numeric unique identifier
    Status - one of: completed, failed, busy, no-answer
    RecordingUrl - link to the call recording (if it exists)
    DateUpdated - time when the call state was updated last
    b'--form-data-boundary-lebu8d9e3h8xzvhf\r\nContent-Disposition: form-data; name="CallSid"\r\n\r\n4c1888cf5d9f430b8dd424dd85aa191f\r\n--form-data-boundary-lebu8d9e3h8xzvhf\r\nContent-Disposition: form-data; name="Status"\r\n\r\ncompleted\r\n--form-data-boundary-lebu8d9e3h8xzvhf\r\nContent-Disposition: form-data; name="DateUpdated"\r\n\r\n2025-01-15 18:14:07\r\n--form-data-boundary-lebu8d9e3h8xzvhf--\r\n\r\n'
    """
    # add any post call hangup processing
    request_form = await request.form()
    logger.info(
        f"Exotel callback request body for call_id: {callback_call_id} is {request_form}",
        call_id=callback_call_id,
    )
    logger.info(
        f"Query params: {request.query_params} \n {update_call_status_url} \n {callback_call_id}",
        call_id=callback_call_id,
    )
    try:
        if update_call_status_url:
            url = update_call_status_url.format(callback_call_id)
            call_status = request_form.get("Status")
            call_sid = request_form.get("CallSid")
            # Delete call config using helper function
            await delete_call_config(callback_call_id)
            transcript = get_transcript_url(callback_call_id)
            logger.info(
                f"Status update payload: url {url}; callback_call_id {callback_call_id}, {call_status}, {call_sid}",
                call_id=callback_call_id,
            )
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    url,
                    json={
                        "call_id": callback_call_id,
                        "status": call_status,
                        "call_provider": "exotel",
                        "call_provider_call_id": call_sid,
                        "transcript": transcript,
                    },
                ) as response:
                    logger.info(
                        "Got response for exotel_hangup_callback to backend",
                        call_id=callback_call_id,
                    )
                    if response.status == 200:
                        response_json = await response.json()
                        res_message = response_json.get("message", "no message found")
                    else:
                        response_text = await response.text()
                        res_message = f"{response_text}"
                    res_message = res_message.replace("{", "").replace("}", "")
                    logger.info(
                        f"Hangup callback Response status: {response.status}, Response body {res_message}",
                        call_id=callback_call_id,
                    )
    except Exception as e:
        logger.error("Error in hangup callback", flush=True, call_id=callback_call_id)
        traceback.print_exc()
    try:
        if callback_call_id:
            websocket = websocket_connections.get(callback_call_id)
            if websocket:
                await websocket.close()
                logger.info(
                    f"WebSocket connection closed for callback_call_id: {callback_call_id}",
                    call_id=callback_call_id,
                )
                del websocket_connections[callback_call_id]
    except Exception as e:
        logger.error("Websocket might be already closed", call_id=callback_call_id)

    return PlainTextResponse("", status_code=200)


@router.post("/cache_test_mp3")
async def put_file_on_redis_api():
    """
    API to cache test_cache.mp3 in Redis using put_file_on_redis.
    """
    global redis_client
    mp3_path = os.path.join(os.path.dirname(__file__), "utils", "test_cache_new.mp3")
    text = "Hello! bro, wassup."
    try:
        # put_file_on_redis expects a filename, not bytes
        key = await put_file_on_redis(redis_client, text, mp3_path)
    except Exception as e:
        logger.error(f"Failed to cache mp3 file: {e}")
        raise HTTPException(status_code=500, detail="Failed to cache MP3 file.")
    return {"redis_key": key}


@router.get("/get_tts_file")
async def get_tts_file_api(text: str = Query(...)):
    """
    API endpoint to retrieve a cached TTS file from Redis and save it locally.
    """
    print("text", text)
    global redis_client
    if not redis_client:
        raise HTTPException(status_code=503, detail="Redis client not available")

    try:
        file_path = await get_tts_file_from_redis(redis_client, text)
        if file_path:
            return {"status": "success", "file_path": file_path}
        else:
            # Distinguish between "not found" and other errors if needed
            # For now, assume None means not found in cache
            raise HTTPException(
                status_code=404, detail=f"TTS data for the provided text not found in cache."
            )
    except HTTPException as e:
        # Re-raise HTTPExceptions directly
        raise e
    except Exception as e:
        logger.error(f"Error retrieving TTS file from Redis: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve TTS file from Redis.")


@router.get("/healthcheck")
async def healthcheck():
    if is_shutting_down:
        logger.warning("Health check returning 503 due to shutdown")
        return JSONResponse(
            content={"status": "shutting down"}, status_code=HTTP_503_SERVICE_UNAVAILABLE
        )
    return {"status": "ok"}


# Include the router without the prefix for backward compatibility
app.include_router(router)
# Include the router with the /pc/v1 prefix
app.include_router(router, prefix="/pc/v1")

if __name__ == "__main__":
    print("Executing __main__ block")
    print(f"ENVIRONMENT value: {os.getenv('ENVIRONMENT')}")

    environment = os.getenv("ENVIRONMENT", "development")
    reload = environment == "development" or environment == "local"
    workers = 2 if environment == "production" else 1
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8765,
        reload=reload,
        workers=workers,
        timeout_graceful_shutdown=DOCKER_KILL_TIMEOUT - 10,
    )
