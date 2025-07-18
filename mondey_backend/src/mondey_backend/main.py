from __future__ import annotations

import logging
import pathlib
from contextlib import asynccontextmanager

import sqlparse
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_injectable.decorator import injectable
from sqlalchemy import text

from .databases.mondey import create_mondey_db_and_tables
from .databases.mondey import engine as mondey_engine
from .databases.users import create_user_db_and_tables
from .databases.users import engine as users_engine
from .logging import logger
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


async def import_e2e_test_sql_files():
    async with users_engine.begin() as con:
        for sql_file in app_settings.E2E_TEST_USER_SQL_FILES.split(";"):
            logging.warning(f"Importing e2e test user data from {sql_file}")
            with open(f"{sql_file}") as file:
                queries = sqlparse.split(
                    sqlparse.format(file.read(), strip_comments=True)
                )
                for query in queries:
                    await con.execute(text(query))
                await con.commit()
    with mondey_engine.connect() as con:
        for sql_file in app_settings.E2E_TEST_MONDEY_SQL_FILES.split(";"):
            logging.warning(f"Importing e2e test mondey data from {sql_file}")
            with open(f"{sql_file}") as file:
                queries = sqlparse.split(
                    sqlparse.format(file.read(), strip_comments=True)
                )
                for query in queries:
                    con.execute(text(query))
                con.commit()
    logging.warning("Updating statistics after importing e2e test data")
    await scheduled_update_stats()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_mondey_db_and_tables()
    await create_user_db_and_tables()
    if app_settings.E2E_TEST_USER_SQL_FILES and app_settings.E2E_TEST_MONDEY_SQL_FILES:
        await import_e2e_test_sql_files()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        scheduled_update_stats,
        CronTrigger.from_crontab(app_settings.STATS_CRONTAB),
    )
    scheduler.start()
    yield
    scheduler.shutdown()
    for host, engine in (
        (app_settings.DATABASE_HOST_MONDEYDB, mondey_engine),
        (app_settings.DATABASE_HOST_USERSDB, users_engine),
    ):
        if not host and engine.url.database:
            db_path = pathlib.Path(engine.url.database)
            logging.warning(f"Removing temporary database {db_path}")
            db_path.unlink()
            db_path.parent.rmdir()


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
    app.add_middleware(GZipMiddleware, minimum_size=5000, compresslevel=5)
    app.mount(
        "/static", StaticFiles(directory=app_settings.STATIC_FILES_PATH), name="static"
    )
    return app


def main():
    logging.basicConfig(
        level=app_settings.LOG_LEVEL.upper(),
        format="%(asctime)s.%(msecs)03d :: %(levelname)s :: %(name)s :: %(funcName)s :: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    for db_host in ("DATABASE_HOST_USERSDB", "DATABASE_HOST_MONDEYDB"):
        if not getattr(app_settings, db_host):
            logger.warning(
                f"{db_host} not set. Using temporary sqlite database, all data will be lost when server is stopped."
            )
    sensitive_settings = [
        "SECRET",
        "DATABASE_PASSWORD",
        "SMTP_PASSWORD",
        "DEEPL_API_KEY",
    ]
    for key, value in app_settings:
        logger.info(
            f"{key}: {'****************' if key in sensitive_settings else value}"
        )
    uvicorn.run(
        "mondey_backend.main:create_app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
        reload_dirs=["mondey_backend/src/mondey_backend"]
        if app_settings.RELOAD
        else None,
        log_level=app_settings.LOG_LEVEL,
        forwarded_allow_ips="*",
        factory=True,
    )


if __name__ == "__main__":
    main()
