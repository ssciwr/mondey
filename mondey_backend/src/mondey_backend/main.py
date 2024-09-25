from __future__ import annotations

import logging
import pathlib
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .databases.milestones import create_database
from .databases.users import create_user_db_and_tables
from .routers import admin
from .routers import auth
from .routers import milestones
from .routers import users
from .settings import app_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()
    await create_user_db_and_tables()
    yield


# ensure static files directory exists
pathlib.Path(app_settings.STATIC_FILES_PATH).mkdir(parents=True, exist_ok=True)
app = FastAPI(lifespan=lifespan, title="MONDEY API", root_path="/api")
app.include_router(milestones.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)
app.mount(
    "/static", StaticFiles(directory=app_settings.STATIC_FILES_PATH), name="static"
)
if app_settings.ENABLE_CORS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def main():
    logging.basicConfig(
        level=app_settings.LOG_LEVEL.upper(),
        format="%(asctime)s :: %(levelname)s :: %(name)s :: %(funcName)s :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)
    for key, value in app_settings:
        logger.info(f"{key}: {value if key != 'SECRET' else '****************'}")
    uvicorn.run(
        "mondey_backend.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
        log_level=app_settings.LOG_LEVEL,
    )


if __name__ == "__main__":
    main()
