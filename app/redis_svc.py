import os
import redis
import time
import json
from pydantic import BaseModel
import uuid
from typing import List, Union
from .task_status import TASK_INIT
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", 'redis'), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0))


task_status_keys = ['task_id', 'status', 'timestamp', 'filename']


class TestCaseTask(BaseModel):
    task_id:str
    status:int
    timestamp:int
    filename:str
    extension:str
    content:str

def testcase_task_from_file(filename:str, file_content:str):
    return TestCaseTask(
        task_id=str(uuid.uuid4()),
        status=TASK_INIT,
        timestamp=int(time.time()),
        filename=filename,
        extension=os.path.splitext(filename)[1],
        content=file_content
    )
    

def add_task_to_redis(filename, file_content):
    task = testcase_task_from_file(filename=filename, file_content=file_content)
    with redis_client.pipeline() as pipe:
        pipe.hset(f'task:{task.task_id}', mapping=task.model_dump())
        pipe.zadd('task_index', {task.task_id: task.timestamp})
        pipe.hincrby('task_status_counts', task.status, 1)
        pipe.execute()
        
    return get_task_status(task.task_id)

def change_status_stat(task:TestCaseTask, to_status):
    with redis_client.pipeline() as pipe:
        pipe.hincrby('task_status_counts', task.status, -1)
        task.status = to_status
        pipe.hset(f'task:{task.task_id}', 'status', to_status)  # Set status to 1, indicating running
        pipe.hincrby('task_status_counts', to_status, 1)
        pipe.execute()

def get_task_status(task_id):
    task = redis_client.hmget(f'task:{task_id}', task_status_keys)
    task = {k: v.decode('utf-8') if v else None for k, v in zip(task_status_keys, task)}
    return task

def get_task_result(task_id):
    file_info = redis_client.hgetall(f'rs-{task_id}')
    if not file_info:
        return None, None
    file_content = file_info[b'content']
    file_extension = file_info[b'extension'].decode('utf-8')
    original_filename = file_info[b'original_filename'].decode('utf-8')
    return f"{original_filename}_unittest.{file_extension}", file_content

def get_tasks_by_page(page=1, per_page=10):
    start = (page - 1) * per_page
    end = start + per_page - 1
    task_ids = redis_client.zrevrange('task_index', start, end)
    tasks = []
    for task_id in task_ids:
        task = redis_client.hmget(f'task:{task_id.decode("utf-8")}', task_status_keys)
        task = {k: v.decode('utf-8') if v else None for k, v in zip(task_status_keys, task)}
        tasks.append(task)
    total_tasks = redis_client.zcard('task_index')
    total_pages = (total_tasks + per_page - 1) // per_page
    return {
        'tasks': tasks,
        'page': page,
        'per_page': per_page,
        'total_tasks': total_tasks,
        'total_pages': total_pages
    }



def get_current_task_status():
    status_counts = redis_client.hgetall('task_status_counts')
    return {int(status): int(count) for status, count in status_counts.items()}


def get_task_by_id(task_id)->Union[TestCaseTask, None]:
    task_data = redis_client.hgetall(f'task:{task_id}')
    if task_data:
        task = TestCaseTask(
            task_id=task_data[b'task_id'].decode('utf-8'),
            status=int(task_data[b'status'].decode('utf-8')),
            timestamp=float(task_data[b'timestamp'].decode('utf-8')),
            filename=task_data[b'filename'].decode('utf-8'),
            extension=task_data[b'extension'].decode('utf-8'),
            content=task_data[b'content'].decode('utf-8')
        )
        return task
    return None
    

def store_task_result(task:TestCaseTask, result)->str:
    processed_key = f"rs-{task.task_id}"
    redis_client.hset(processed_key, mapping={
            'content': result,
            'extension': task.extension,
            'original_filename': task.filename
    })
    return processed_key