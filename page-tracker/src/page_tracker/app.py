from flask import Flask
from redis import Redis

app = Flask(__name__)
redis = Redis()

@app.get("/")
def index():
    page_views = redis.incr("page_views")
    return f"This page has been viewed {page_views} times"
