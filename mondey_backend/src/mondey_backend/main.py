from __future__ import annotations

import asyncio
import logging
import pathlib
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_injectable.decorator import injectable

from .databases.mondey import create_mondey_db_and_tables
from .databases.users import create_user_db_and_tables
from .routers import admin
from .routers import auth
from .routers import milestones
from .routers import questions
from .routers import research
from .routers import users
from .settings import app_settings
from .statistics import async_update_stats


async def scheduled_update_stats():
    update_stats_func = injectable(async_update_stats)
    await update_stats_func()
    # Based on async dependency injection here: https://github.com/JasperSui/fastapi-injectable/blob/main/test/test_injectable.py


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_mondey_db_and_tables()
    await create_user_db_and_tables()
    # For manual invocation: await scheduled_update_stats()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        lambda: asyncio.run(
            scheduled_update_stats()
        ),  # Review appreciated of this approach
        CronTrigger.from_crontab(app_settings.STATS_CRONTAB),
    )
    scheduler.start()
    yield
    scheduler.shutdown()


def create_app() -> FastAPI:
    # ensure static files directory exists
    pathlib.Path(app_settings.STATIC_FILES_PATH).mkdir(parents=True, exist_ok=True)
    app = FastAPI(lifespan=lifespan, title="MONDEY API", root_path="/api")
    app.include_router(milestones.create_router())
    app.include_router(questions.create_router())
    app.include_router(admin.create_router())
    app.include_router(users.create_router())
    app.include_router(auth.create_router())
    app.include_router(research.create_router())
    app.mount(
        "/static", StaticFiles(directory=app_settings.STATIC_FILES_PATH), name="static"
    )
    if app_settings.ENABLE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173", "http://localhost:5678"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    return app


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
        "mondey_backend.main:create_app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
        log_level=app_settings.LOG_LEVEL,
        forwarded_allow_ips="*",
        factory=True,
    )


if __name__ == "__main__":
    main()
