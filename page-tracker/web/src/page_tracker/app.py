import os
from functools import cache

from flask import Flask
from redis import Redis, RedisError

app = Flask(__name__)


@app.get("/")
def index():
    try:
        page_views = redis().incr("page_views")
    except RedisError:
        app.logger.exception("Redis Error")
        return "Sorry, something went wrong \N{PENSIVE FACE}", 500
    else:
        message = f"🎉 This page has been viewed {page_views} times! "
        message += "Thanks for visiting!"
        return message


@cache
def redis():
    return Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
