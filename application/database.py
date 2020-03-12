import redis

db = redis.Redis(host = "redis", port = 6379, decode_responses=True)