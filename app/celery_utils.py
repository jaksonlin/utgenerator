from celery import Celery
import os

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery

def easy_celery():
    celery = Celery(
        'tasks',
        backend=os.getenv('CELERY_RESULT_BACKEND','redis://localhost:6379/0'),
        broker=os.getenv('CELERY_BROKER_URL','redis://localhost:6379/0'),
    )
    celery.conf.update(
        task_default_queue='unittest_generation',
        task_routes={'app.task_management.generate_unittest_task': {'queue': 'unittest_generation'}},
        worker_prefetch_multiplier=1,
        worker_concurrency=1,
    )
    return celery


