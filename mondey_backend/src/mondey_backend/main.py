from __future__ import annotations

import logging
import pathlib
import time
from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

from .databases.mondey import create_mondey_db_and_tables
from .databases.mondey import engine
from .databases.users import create_user_db_and_tables
from .routers import admin
from .routers import auth
from .routers import milestones
from .routers import questions
from .routers import research
from .routers import users
from .routers.utils import recompute_milestone_statistics
from .routers.utils import recompute_milestonegroup_statistics
from .settings import app_settings


def recompute_statistics():
    while True:
        with Session(engine) as session:
            try:
                with session.begin():
                    recompute_milestone_statistics(session)
                    recompute_milestonegroup_statistics(session)
                    print("Recomputing statistics")
            except OperationalError as e:
                print(f"Error acquiring lock: {e}")
            finally:
                session.commit()

        # sleep until next run - 3:00 AM the week after
        now = datetime.now()
        next_run = (now + timedelta(days=7)).replace(
            hour=3, minute=0, second=0, microsecond=0
        )
        sleep_duration = (next_run - now).total_seconds()
        time.sleep(sleep_duration)  # 1 week. needs to be put into config


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_mondey_db_and_tables()
    await create_user_db_and_tables()

    # run the statistics recomputation in a separate process
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        recompute_statistics, "cron", hour=3, minute=0, day_of_week="mon"
    )  # Every Monday at 3:00 AM
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
