import redis
import os

_REDIS_HOST = os.getenv("REDIS_HOST")
_REDIS_PORT = int(os.getenv("REDIS_PORT"))
_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
# add this in production "or not _REDIS_PASSWORD"
if not _REDIS_HOST or not _REDIS_PORT :
    raise ValueError("REDIS configeration not found in environment variables.")

# Connect to Redis
redis_client = redis.Redis(
    host=_REDIS_HOST,
    port=_REDIS_PORT,
    password=_REDIS_PASSWORD,
    db=0,
    decode_responses=True # Ensure strings are returned as strings
)

def check_redis_connection() -> bool:
    try:
        redis_client.ping()
        print("✅✅✅✅ Redis connection successful.")
        return True
    except redis.exceptions.RedisError:
        print("❌❌❌❌ Redis connection failed.")
        return False

if not check_redis_connection():
    raise ValueError("Redis connection failed.")
