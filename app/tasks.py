import logging
from datetime import datetime

from .celery_utils import make_celery, easy_celery
celery = easy_celery()


def get_celery_stat():
    inspect = celery.control.inspect()
    active = inspect.active()
    reserved = inspect.reserved()
    scheduled = inspect.scheduled()
    registered = inspect.registered()
    revoked = inspect.revoked()
    stats = inspect.stats()
    
    if active is not None and reserved is not None:
        active_count = sum(len(tasks) for tasks in active.values())
        reserved_count = sum(len(tasks) for tasks in reserved.values())
        return {
            'active_tasks': active_count,
            'queued_tasks': reserved_count,
            'scheduled_tasks': sum(len(tasks) for tasks in scheduled.values()) if scheduled else 0,
            'registered_tasks': sum(len(tasks) for tasks in registered.values()) if registered else 0,
            'revoked_tasks': sum(len(tasks) for tasks in revoked.values()) if revoked else 0,
            'worker_stats': stats
        }
    return None

@celery.task
def hello_world_task(task_id):
    try:
        logging.debug(f"Starting hello task {task_id} at {datetime.now()}")
        logging.debug(f"End hello task {task_id} at {datetime.now()}")
        return 'Hello, World!'
    except Exception as e:
        logging.error(f"Task {task_id} failed at {datetime.now()}: {str(e)}")
        return {'status': 'failed', 'error': str(e)}

@celery.task
def generate_unittest_task(file_path, task_id):
    import os
    from .models import ModelManager
    try:
        logging.debug(f"Starting task {task_id} at {datetime.now()}")
        os.makedirs(os.getenv('DOWNLOAD_FOLDER'), exist_ok=True)
        with open(file_path, 'r') as file:
            code = file.read()
        model_manager = ModelManager.get_model_manager()
        all_tests = model_manager.generate_unittest(code)
        output_path = os.path.join(os.getenv('DOWNLOAD_FOLDER'), f"{task_id}_unittest.py")
        with open(output_path, 'w') as file:
            for test in all_tests:
                file.write(test.model_dump_json() + '\n')
        logging.debug(f"Completed task {task_id} at {datetime.now()}")
        return {'status': 'completed', 'output_path': output_path}
    except Exception as e:
        logging.error(f"Task {task_id} failed at {datetime.now()}: {str(e)}")
        return {'status': 'failed', 'error': str(e)}