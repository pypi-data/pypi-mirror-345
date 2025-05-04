base_tools = [  # noqa: D100
    {
        "name": "end_call",
        "description": "End the current call when the conversation has reached a natural conclusion or user says bye or tells to cut the call or speak with you later as they are busy.",
        "parameters": {
            "type": "object",
            "properties": {
                "final_message": {
                    "type": "string",
                    "description": "The final message to say to the user before ending the call. Should be a polite goodbye message appropriate for the conversation context. Keep is short and less than 15 words.",
                }
            },
            "required": ["final_message"],
        },
    }
]


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
