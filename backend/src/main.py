from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk import init as sentry_init
from apscheduler.schedulers.background import BackgroundScheduler
from .auth.router import router as auth_router
from .news.router import router as news_router
from .pricing.router import router as pricing_router
from .database import SessionLocal
from .news.service import fetch_and_process_news
from .news.models import NewsArticle 
from .config import settings

sentry_init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=settings.TRACES_SAMPLE_RATE,
    profiles_sample_rate=settings.PROFILES_SAMPLE_RATE,
)

app = FastAPI()

schedulers = BackgroundScheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def start_scheduler():
    db = SessionLocal()
    if db.query(NewsArticle).count() == 0:
        fetch_and_process_news()
    db.close()
    schedulers.add_job(fetch_and_process_news, "interval", minutes=settings.FETCH_NEWS_INTERVAL_MINUTES)
    schedulers.start()

@app.on_event("shutdown")
def shutdown_scheduler():
    schedulers.shutdown()

app.include_router(auth_router, prefix="/api/v1")
app.include_router(news_router, prefix="/api/v1")
app.include_router(pricing_router, prefix="/api/v1")