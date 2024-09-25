import os
import redis


redis_client = redis.Redis(host=os.getenv("REDIS_HOST", 'redis'), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0))



