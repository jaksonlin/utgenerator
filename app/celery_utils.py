from celery import Celery
import os

def get_redis_conn():
    host = os.getenv("REDIS_HOST", 'redis')
    port = os.getenv("REDIS_PORT", 6379)
    db = os.getenv("REDIS_DB", 0)
    return f"redis://{host}:{port}/{db}"

def easy_celery():
    redis_default = get_redis_conn()
    celery = Celery(
        'tasks',
        backend=os.getenv('CELERY_RESULT_BACKEND',redis_default),
        broker=os.getenv('CELERY_BROKER_URL',redis_default),
    )
    celery.conf.update(
        task_default_queue='unittest_generation',
        task_routes={'app.task_management.generate_unittest_task': {'queue': 'unittest_generation'}},
        worker_prefetch_multiplier=1,
        worker_concurrency=1,
    )
    return celery


