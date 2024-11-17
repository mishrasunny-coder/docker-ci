from flask import Flask
from redis import Redis
from functools import cache

app = Flask(__name__)

@app.get("/")
def index():
    page_views = redis().incr("page_views")
    return f"This page has been viewed {page_views} times"

@cache
def redis():
    return Redis()