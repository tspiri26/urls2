import os
import random
import re
import string
import logging

import aioredis
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from flask import Flask
import redis

# #####################ADDED CODE############################################
# app = Flask(__name__)

# redis_host = os.environ.get('REDISHOST', 'localhost')
# redis_port = int(os.environ.get('REDISPORT', 6379))
# redis_client = redis.StrictRedis(host=redis_host, port=redis_port)


# #####################ADDED CODE############################################

REDIS_URL= "http://10.247.143.251/1"


db = aioredis.from_url(os.getenv("REDIS_URL")
                       or "redis://localhost/1", decode_responses=True)

templates = Jinja2Templates(directory="templates")
is_url = re.compile(
    r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')

app = FastAPI(
    title='UrlShorter',
    version='6.9'
)


@app.get('/')
async def main_html(rq: Request):
    return templates.TemplateResponse("index.html", {"request": rq, "hostname": os.uname().nodename})


@app.get('/create')
async def create(rq: Request, link: str):
    if not is_url.match(link):
        return templates.TemplateResponse("message.html", {"request": rq, "message": "Not a valid url"}, 404)
    n = 4
    while True:
        shrt = ''.join(random.choice(string.ascii_letters) for _ in range(n))
        if not await db.get(shrt):
            break
        n += 1
    await db.set(shrt, link)
    return templates.TemplateResponse("success.html",
                                      {"request": rq,
                                       "link": f"http://{rq.url.hostname}{':'+ str(rq.base_url.port) if rq.base_url.port else ''}/{shrt}"
                                       })


@app.get('/{shrt}')
async def create(rq: Request, shrt: str):
    u = await db.get(shrt)
    if u:
        return RedirectResponse(u)
    return templates.TemplateResponse("message.html", {"request": rq, "message": "404: Not found"}, 404)
