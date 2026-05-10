"""Celery task entry points for aftercare checkpoints and the daily monitor.

Each task instantiates its agent with settings, then runs the async .run()
inside asyncio.run(). The Celery worker process and the FastAPI process share
the same Supabase service-role client.
"""
import asyncio

import structlog

from app.config import settings
from app.database import get_supabase
from app.workers.celery_app import celery_app
from app.agents.aftercare.day7_agent import Day7Agent
from app.agents.aftercare.day30_agent import Day30Agent
from app.agents.aftercare.day90_agent import Day90Agent
from app.agents.aftercare.monitor_agent import MonitorAgent

log = structlog.get_logger()


@celery_app.task(name="app.workers.tasks.run_day7_check")
def run_day7_check(job_id: str) -> dict:
    log.info("celery.day7_check.start", job_id=job_id)
    db = get_supabase()
    agent = Day7Agent(
        db,
        access_token=settings.google_access_token,
        dataforseo_login=settings.dataforseo_login,
        dataforseo_password=settings.dataforseo_password,
    )
    return asyncio.run(agent.run(job_id))


@celery_app.task(name="app.workers.tasks.run_day30_check")
def run_day30_check(job_id: str) -> dict:
    log.info("celery.day30_check.start", job_id=job_id)
    db = get_supabase()
    agent = Day30Agent(
        db,
        access_token=settings.google_access_token,
        dataforseo_login=settings.dataforseo_login,
        dataforseo_password=settings.dataforseo_password,
        ahrefs_api_key=settings.ahrefs_api_key,
    )
    return asyncio.run(agent.run(job_id))


@celery_app.task(name="app.workers.tasks.run_day90_check")
def run_day90_check(job_id: str) -> dict:
    log.info("celery.day90_check.start", job_id=job_id)
    db = get_supabase()
    agent = Day90Agent(
        db,
        access_token=settings.google_access_token,
        dataforseo_login=settings.dataforseo_login,
        dataforseo_password=settings.dataforseo_password,
        ahrefs_api_key=settings.ahrefs_api_key,
        anthropic_api_key=settings.anthropic_api_key,
    )
    return asyncio.run(agent.run(job_id))


@celery_app.task(name="app.workers.tasks.run_monitor")
def run_monitor() -> dict:
    log.info("celery.monitor.start")
    db = get_supabase()
    agent = MonitorAgent(
        db,
        dataforseo_login=settings.dataforseo_login,
        dataforseo_password=settings.dataforseo_password,
    )
    return asyncio.run(agent.run())
