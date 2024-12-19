from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk import init as sentry_init
from apscheduler.schedulers.background import BackgroundScheduler
from src.services.exceptions_handler import APIException
from .users.router import router as user_router
from .news.router import router as news_router
from .pricing.router import router as pricing_router
from .database import SessionLocal
from .news.service import fetch_and_process_news
from .news.models import NewsArticle 
from .config import global_config
from src.services.logger import app_logger
from src.services.exceptions_handler import InternalServerErrorException

sentry_init(
    dsn=global_config.SENTRY_DSN,
    traces_sample_rate=global_config.TRACES_SAMPLE_RATE,
    profiles_sample_rate=global_config.PROFILES_SAMPLE_RATE,
)

app = FastAPI()

schedulers = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[global_config.CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def start_scheduler():
    app_logger.app_startup()
    try:
        db = SessionLocal()
        if db.query(NewsArticle).count() == 0:
            fetch_and_process_news()
        db.close()
        schedulers.add_job(fetch_and_process_news, "interval", minutes=global_config.FETCH_NEWS_INTERVAL_MINUTES)
        schedulers.start()
        app_logger.scheduler_started()
    except Exception as e:
        app_logger.fetch_news_job_failed(e)
        raise InternalServerErrorException(e)

@app.on_event("shutdown")
def shutdown_scheduler():
    app_logger.app_shutdown()
    try:
        schedulers.shutdown()
        app_logger.scheduler_shutdown()
    except Exception as e:
        app_logger.fetch_news_job_failed(e)
        raise InternalServerErrorException(e)

app.include_router(user_router, prefix=global_config.API_PREFIX)
app.include_router(news_router, prefix=global_config.API_PREFIX)
app.include_router(pricing_router, prefix=global_config.API_PREFIX)

@app.exception_handler(APIException)
async def api_exception_handler(request, exc: APIException):
    exc.handle()
    return exc.to_response()