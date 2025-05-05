from redis.asyncio.client import Redis

async def scan_keys(redis_client: Redis, match_pattern: str):
    cursor = 0  # Initial cursor
    keys = []   # To collect all matching keys

    # Loop until the cursor returns to 0, which indicates completion
    while True:
        cursor, batch = await redis_client.scan(cursor=cursor, match=match_pattern)
        keys.extend(batch)  # Collect the batch of keys
        
        if cursor == 0:
            break

    return keys
