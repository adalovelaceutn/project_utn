from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.crud_kolb_profiles import ensure_kolb_indexes
from app.crud_users import ensure_user_indexes
from app.database import close_mongo_connection, connect_to_mongo
from app.routers.auth import router as auth_router
from app.routers.kolb_profiles import router as kolb_profiles_router
from app.routers.users import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    await ensure_user_indexes()
    await ensure_kolb_indexes()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Kolb Profile API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://10.0.0.165:4200",
        "http://0.0.0.0:4200",
        "https://potential-spork-5gwxjpw55vwqfqj-4200.app.github.dev",
        "https://potential-spork-5gwxjpw55vwqfqj-8000.app.github.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(kolb_profiles_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
