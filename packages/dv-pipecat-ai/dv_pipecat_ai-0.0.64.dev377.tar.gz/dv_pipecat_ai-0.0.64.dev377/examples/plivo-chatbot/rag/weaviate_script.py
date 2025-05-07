import os

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

load_dotenv(override=True)


def get_weaviate_client():
    return weaviate.use_async_with_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_CLUSTER_URI"),
        auth_credentials=Auth.api_key(os.getenv("WEAVIATE_CLUSTER_API_KEY")),
        headers={"X-Openai-Api-Key": os.getenv("OPENAI_API_KEY")},
    )
