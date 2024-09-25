import logging
from datetime import datetime
from .redis_svc import redis_client
from .celery_utils import easy_celery
import json
celery = easy_celery()
from celery.exceptions import TimeoutError

def get_celery_stat(timeout=5.0):
    try:
        inspect = celery.control.inspect(timeout=timeout)
        active = inspect.active()
        reserved = inspect.reserved()
        scheduled = inspect.scheduled()
        registered = inspect.registered()
        revoked = inspect.revoked()
        stats = inspect.stats()
        
        if all(x is not None for x in [active, reserved, scheduled, registered, revoked, stats]):
            return {
                'status': 'available',
                'active_tasks': sum(len(tasks) for tasks in active.values()),
                'queued_tasks': sum(len(tasks) for tasks in reserved.values()),
                'scheduled_tasks': sum(len(tasks) for tasks in scheduled.values()),
                'registered_tasks': sum(len(tasks) for tasks in registered.values()),
                'revoked_tasks': sum(len(tasks) for tasks in revoked.values()),
                'worker_stats': stats
            }
        else:
            return {
                'status': 'partially_available',
                'active_tasks': sum(len(tasks) for tasks in (active or {}).values()),
                'queued_tasks': sum(len(tasks) for tasks in (reserved or {}).values()),
                'scheduled_tasks': sum(len(tasks) for tasks in (scheduled or {}).values()),
                'registered_tasks': sum(len(tasks) for tasks in (registered or {}).values()),
                'revoked_tasks': sum(len(tasks) for tasks in (revoked or {}).values()),
                'worker_stats': stats or {},
                'message': 'Some Celery inspection data is unavailable. The system might be under heavy load.'
            }
    except TimeoutError:
        return {
            'status': 'timeout',
            'message': 'Celery inspection timed out. The system might be under heavy load.'
        }
    except Exception as e:
        logging.error(f"Error in get_celery_stat: {str(e)}")
        return {
            'status': 'error',
            'message': f'An unexpected error occurred while fetching Celery status: {str(e)}'
        }

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
        _, file_extension = os.path.splitext(file_path)
        output_path = os.path.join(os.getenv('DOWNLOAD_FOLDER'), f"{task_id}_unittest{file_extension}")
        with open(output_path, 'w') as file:
            for test in all_tests:
                file.write(test.model_dump_json() + '\n')
        logging.debug(f"Completed task {task_id} at {datetime.now()}")
        return {'status': 'completed', 'output_path': output_path}
    except Exception as e:
        logging.error(f"Task {task_id} failed at {datetime.now()}: {str(e)}")
        return {'status': 'failed', 'error': str(e)}
    
@celery.task
def generate_unittest_task_from_redis(task_id):
    import os
    from .models import ModelManager
    try:
        logging.debug(f"Starting task {task_id} at {datetime.now()}")
        file_info = redis_client.hgetall(task_id)
        if not file_info:
            return 'File not found'
        
        file_content = file_info[b'content'].decode('utf-8')
        file_extension = file_info[b'extension'].decode('utf-8')
        file_name = file_info[b'original_filename'].decode('utf-8')
        # write file for track
        output_path = os.path.join(os.getenv('UPLOAD_FOLDER'), f"{task_id}_unittest{file_extension}")
        with open(output_path, 'w') as file:
            file.write(str(file_content))
        
        # Process the file content (example processing)
        model_manager = ModelManager.get_model_manager()
        all_tests = model_manager.generate_unittest(file_content)
        result_json = json.dumps([test.model_dump() for test in all_tests])

        processed_key = f"rs-{task_id}"
        redis_client.hset(processed_key, mapping={
                'content': result_json,
                'extension': file_extension,
                'original_filename': file_name
        })

        # write file for track
        output_path = os.path.join(os.getenv('DOWNLOAD_FOLDER'), f"{task_id}_unittest_{file_extension}.json")
        with open(output_path, 'w') as file:
            file.write(result_json)

        logging.debug(f"Completed task {task_id} at {datetime.now()}")
        return {'status': 'completed', 'output_path': f'{processed_key}'}
    except Exception as e:
        logging.error(f"Task {task_id} failed at {datetime.now()}: {str(e)}")
        return {'status': 'failed', 'error': str(e)}