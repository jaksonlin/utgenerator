# celery_worker.py
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Now that environment variables are loaded, import and start Celery
from app.routes.task_management import celery

if __name__ == '__main__':
    celery.worker_main(['worker', '--loglevel=info', '--concurrency=1', '-Q', 'unittest_generation'])