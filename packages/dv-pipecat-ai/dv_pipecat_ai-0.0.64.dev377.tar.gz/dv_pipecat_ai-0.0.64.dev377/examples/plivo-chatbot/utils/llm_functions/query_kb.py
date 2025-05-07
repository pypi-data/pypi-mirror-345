import random
import time

from weaviate.classes.query import Filter


async def query_knowledge_base(
    function_name,
    tool_call_id,
    arguments,
    tts,
    pre_query_phrases,
    kb_name_to_id_map,
    weaviate_client,
    collection_name,
    result_callback,
    function_call_monitor,
    logger,
):
    function_call_monitor.append("query_knowledge_base_called")
    phrase = random.choice(pre_query_phrases)
    await tts.say(phrase)
    logger.info(f"Querying knowledge base for question {tool_call_id}: {arguments['question']}")
    question = arguments["question"]
    formatting_instructions = (
        "Format the result in a concise answer. The number of words should be less than 50 words. "
        "Answer only to the query which user asked and don't add anything extra. "
        "Also convert numbers to words as needed. query-> "
    )
    formatting_instructions += question
    kb_id = kb_name_to_id_map[arguments["rag_file_name"]]
    start = time.perf_counter()

    collection = weaviate_client.collections.get(collection_name)
    response = await collection.query.near_text(
        query=question,
        limit=3,
        distance=0.7,
        filters=Filter.by_property("knowledge_base_id").equal(kb_id),
    )
    end = time.perf_counter()
    logger.info(f"Time taken for kb query {tool_call_id}: {end - start:.2f} seconds")
    if len(response.objects) == 0:
        answer = "I am sorry I couldn't find anything!"
    else:
        answer_list = list()
        for object_ in response.objects:
            answer_list.append(object_.properties["chunk"])
        answer = "\n".join(answer_list)

    await result_callback(answer)
