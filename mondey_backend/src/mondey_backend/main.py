from __future__ import annotations

import logging
import pathlib
from contextlib import asynccontextmanager

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_injectable.util import get_injected_obj

from .databases.mondey import create_mondey_db_and_tables
from .databases.users import create_user_db_and_tables
from .routers import admin
from .routers import auth
from .routers import milestones
from .routers import questions
from .routers import research
from .routers import users
from .settings import app_settings
from .statistics import update_stats


def scheduled_update_stats():
    return get_injected_obj(update_stats)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_mondey_db_and_tables()
    await create_user_db_and_tables()
    scheduler = AsyncIOScheduler()
    print(f'crontab shit: {app_settings.STATS_CRONTAB}')
    cronexpr = app_settings.STATS_CRONTAB.replace('\"','\'').replace('mon', '1')
    scheduler.add_job(
        scheduled_update_stats,
        CronTrigger.from_crontab(cronexpr),
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
            allow_origins=["http://localhost:5173"],
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
