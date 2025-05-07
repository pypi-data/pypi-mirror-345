import aiohttp
from env_config import api_config

from ..transcript import TranscriptHandler, store_transcript  # noqa: D100


async def fetch_column_value(table_name: str, primary_id: str, column_name: list[str], logger):
    logger.info(f"Fetching column value for call {primary_id} from table {table_name}")
    url = f"{api_config.CALLING_BACKEND_URL}/external_hook/fetch_column_value"
    payload = {"table_name": table_name, "column_info": {"id": primary_id, "values": column_name}}
    headers = {
        "X-API-KEY": api_config.CALLING_BACKEND_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                if response.status != 200:
                    logger.error(
                        "Failed API call. Status: {}, Response: {}",
                        response.status,
                        await response.text(),
                    )
                    return {}
                response_data = await response.json()
                return response_data
    except Exception as e:
        logger.exception(f"Error in fetch_column_value: {str(e)}")
        return {}


async def update_db(table_name: str, primary_id: str, column_values: dict[str, any], logger):
    url = f"{api_config.CALLING_BACKEND_URL}/external_hook/update_db"

    payload = {
        "table_name": table_name,
        "update_info": [{"id": primary_id, "values": column_values}],
    }

    headers = {
        "X-API-KEY": api_config.CALLING_BACKEND_API_KEY,
        "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                return True
            else:
                logger.error(f"{primary_id} Failed to update db: {response.text}")
                return False


async def cleanup_connection(
    callback_call_id,
    context_aggregator,
    transcript_handler: TranscriptHandler,
    task,
    task_references,
    function_call_monitor,
    logger,
    record_locally=False,
):
    logger.info(f"Performing connection cleanup for {callback_call_id}", call_id=callback_call_id)
    # await task.queue_frame(CancelFrame())
    await task.cancel()
    if transcript_handler.messages:
        history = [
            {"role": msg.role, "content": msg.content} for msg in transcript_handler.messages
        ]
    else:
        history = context_aggregator.assistant().context.get_messages_for_persistent_storage()

    await store_transcript(callback_call_id, history, record_locally)
    logger.debug(f"Stored transcript with length: {len(history)}", call_id=callback_call_id)
    # await task.queue_frame(CancelFrame())
    # await task.cancel()
    for t in task_references:
        logger.debug("Cancelling new bot tasks", call_id=callback_call_id)
        t.cancel()
    task_references.clear()
    if function_call_monitor:
        function_call_monitor_dict = {i: True for i in list(set(function_call_monitor))}
        print("function_call_monitor_dict", function_call_monitor_dict)
        logger.info("updating db for all function calls: {}", function_call_monitor_dict)
        current_analysis_value = await fetch_column_value(
            "calls", callback_call_id, ["analysis"], logger
        )
        current_analysis_value = await fetch_column_value("calls", callback_call_id, ["analysis"], logger)
        if current_analysis_value.get("data"):
            current_analysis_value = current_analysis_value["data"][0]["analysis"]
            current_analysis_value.update(function_call_monitor_dict)
            update_db_response = await update_db(
                "calls", callback_call_id, {"analysis": current_analysis_value}, logger
            )
            logger.info(
                "Update db response for id: {}", update_db_response, call_id=callback_call_id
            )
        else:
            logger.error(f"Failed to fetch column value for id {callback_call_id} ")
