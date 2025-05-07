import os


rag_tool = {
    "name": "query_knowledge_base",
    "description": (
        "Retrieve and synthesize a concise answer from the knowledge base based on the given question. "
        "The input should include detailed context and any relevant keywords to enable accurate and targeted search results. "
        "This tool uses a retrieval-augmented generation approach to extract key information from stored records, so providing maximum relevant details will improve the quality of the generated answer."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": (
                    "The question to query the knowledge base with. Include as much context and specific details as possible "
                    "to ensure that the retrieval-augmented generation process can fetch the most relevant records and generate an accurate answer."
                ),
            },
            "rag_file_name": {
                "type": "string",
                "description": (
                    "The name of the file that contains the knowledge base to search in order to answer the question. "
                    "Ensure the correct file is referenced to get relevant results."
                ),
            },
        },
        "required": ["question", "rag_file_name"],
    },
}


def get_rag_content(workspace_id, file_name):
    """Get the RAG content from the file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rag_content_path = os.path.join(script_dir, "workspaces_data", workspace_id, file_name)
    with open(rag_content_path, "r") as f:
        return f.read()


RAG_CONTENT_MAP = {}


def get_rag_prompt(workspace_id, file_name):
    unique_key = f"{workspace_id}_{file_name}"
    if RAG_CONTENT_MAP[unique_key]:
        RAG_CONTENT = RAG_CONTENT_MAP[unique_key]
    else:
        RAG_CONTENT = get_rag_content(workspace_id, file_name)
        RAG_CONTENT_MAP[unique_key] = RAG_CONTENT

    RAG_PROMPT = f"""
    You are a helpful assistant designed to answer user questions based solely on the provided knowledge base.
    **Instructions:**
    1.  **Knowledge Base Only:** Answer questions *exclusively* using the information in the "Knowledge Base" section below. Do not use any outside information.
    2.  **Conversation History:** Use the "Conversation History" (ordered oldest to newest) to understand the context of the current question.
    3.  **Concise Response:**  Respond in 50 words or fewer.  The response will be spoken, so avoid symbols, abbreviations, or complex formatting. Use plain, natural language.
    4.  **Unknown Answer:** If the answer is not found within the "Knowledge Base," respond with "I don't know." Do not guess or make up an answer.
    5. Do not introduce your response. Just provide the answer.
    6. You must follow all instructions.

    **Input Format:**
    Each request will include:
    *   **Conversation History:**  (A list of previous user and assistant messages, if any)

    **Information about the knowledge base -> **\n
    The best zones are the one's which have the highest bonus.
    21day_orders mean the minimum number of orders partner has to do to earn the bonus. \n
    21day_bonus means that they will get this amount if they complete the 21day_orders.\n
    Nearest_zone signifies the best possible zones near the zone enquired by the callee.\n

    **Knowledge Base:**
    Here is the knowledge base you have access to:
    ```
    {RAG_CONTENT}
    ```
    """

    print("here is the rag_prompt", RAG_PROMPT)

    return RAG_PROMPT
