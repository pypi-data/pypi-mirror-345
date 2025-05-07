# weaviate_client.py
import os

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

load_dotenv(override=True)


class WeaviateClientManager:
    def __init__(self):
        self.client = None
        self.is_connected = False

    async def connect(self):
        if not self.is_connected:
            self.client = weaviate.use_async_with_weaviate_cloud(
                cluster_url=os.getenv("WEAVIATE_CLUSTER_URI"),
                auth_credentials=Auth.api_key(os.getenv("WEAVIATE_CLUSTER_API_KEY")),
                headers={"X-Openai-Api-Key": os.getenv("OPENAI_API_KEY")},
            )
            await self.client.connect()
            self.is_connected = True

    async def close(self):
        if self.is_connected:
            await self.client.close()
            self.is_connected = False

    def get_client(self):
        if not self.is_connected:
            raise RuntimeError("Weaviate client not connected")
        return self.client


# Shared instance (safe because each worker process gets its own copy)
weaviate_client_manager = WeaviateClientManager()
