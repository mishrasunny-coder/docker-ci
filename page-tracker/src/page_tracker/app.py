from flask import Flask
from redis import Redis, RedisError
from functools import cache


app = Flask(__name__)

@app.get("/")
def index():
    try:
        page_views = redis().incr("page_views")
    except RedisError:
        app.logger.exception("Redis Error")
        return "Sorry, something went wrong \N{pensive face}", 500
    else:
        return f"This page has been viewed {page_views} times"

@cache
def redis():
    return Redis()