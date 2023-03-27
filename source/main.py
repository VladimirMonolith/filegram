import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from authentication.config import auth_backend
from authentication.manager import fastapi_users
from authentication.schemas import UserCreate, UserRead, UserUpdate
from content.routers import router as content_router
from tasks.routers import router as tasks_router

app = FastAPI(title='Filegram')


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix='/auth',
    tags=['auth'],
)

app.include_router(
    fastapi_users.get_users_router(
        UserRead, UserUpdate, requires_verification=True
    ),
    prefix='/users',
    tags=['users'],
)

app.include_router(content_router)
app.include_router(tasks_router)


origins = [
    # адрес фронта,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        'GET', 'POST', 'PATCH', 'PUT', 'OPTIONS', 'DELETE', 'OPTIONS'
    ],
    allow_headers=[
        'Content-Type', 'Set-Cookie', 'Access-Control-Allow-Headers',
        'Access-Control-Allow-Origin', 'Authorization'
    ],
)


@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers['X-Process-Time'] = str(process_time)
    return response


@app.on_event('startup')
async def startup():
    redis = aioredis.from_url(
        'redis://localhost', encoding='utf8', decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix='fastapi-cache')
    