from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.database import (
    create_db_pool,
    close_db_pool,
)
from backend.routers.dashboard import (router as dashboard_router)
from backend.routers.search import (router as search_router)

from backend.routers.analysis import (
    router as analysis_router,
)

from backend.routers.layers import (
    router as layers_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await create_db_pool()

    yield

    await close_db_pool()


app = FastAPI(
    title="Infrastructure Gap Mapping API",
    lifespan=lifespan,
)


origins = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

app.include_router(search_router)

app.include_router(analysis_router)

app.include_router(layers_router)

app.include_router(dashboard_router)