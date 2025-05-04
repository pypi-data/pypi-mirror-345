import aiocache  # type: ignore  # noqa: D100

# Create cache instance
cache = aiocache.Cache(aiocache.SimpleMemoryCache)
