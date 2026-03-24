import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import cluster as cluster_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Amazon Cluster API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cluster_router.router, prefix="/api", tags=["cluster"])


@app.middleware("http")
async def log_requests(request, call_next):
    log.info("Request %s %s", request.method, request.url.path)
    try:
        response = await call_next(request)
        log.info("Response %s %s -> %s", request.method, request.url.path, response.status_code)
        return response
    except Exception as e:
        log.exception("Error handling %s %s: %s", request.method, request.url.path, e)
        raise
