import logging
from datetime import datetime
from .redis_svc import change_status_stat, get_task_by_id, store_task_result
from .celery_utils import easy_celery
import json
import os
from .models import ModelManager

celery = easy_celery()
from .task_status import *

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
    
    try:
        task = get_task_by_id(task_id)
        if task is None:
            return 'File not found'
        logging.debug(f"Starting task {task_id} at {datetime.now()}")
        
        change_status_stat(task, TASK_RUN)
        
        # Process the file content (example processing)
        model_manager = ModelManager.get_model_manager()

        all_tests = model_manager.generate_unittest(task.content)

        result_json = json.dumps([test.model_dump() for test in all_tests])

        processed_key = store_task_result(task, result_json)

        change_status_stat(task, TASK_SUCC)

        logging.debug(f"Completed task {task_id} at {datetime.now()}")
        return {'status': 'completed', 'output_path': f'{processed_key}'}
    
    except Exception as e:

        change_status_stat(task, TASK_FAIL)
        logging.error(f"Task {task_id} failed at {datetime.now()}: {str(e)}")
        return {'status': 'failed', 'error': str(e)}