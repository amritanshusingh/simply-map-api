from celery import Celery
from app.core.config import settings

celery_app = Celery(
    'geospatial_api',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    'app.services.generate_ops.*': {'queue': 'generate'},
    'app.services.calculate_ops.*': {'queue': 'calculate'},
}
