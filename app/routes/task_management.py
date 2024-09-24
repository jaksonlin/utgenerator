from celery import Celery
import os
from dotenv import load_dotenv
load_dotenv()
celery = Celery('tasks', 
                broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
                backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'))
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import uuid

import tempfile
from app.models.model_manager import model_manager
from celery.app.control import Inspect
from flask import current_app

task_management_bp = Blueprint('task_management', __name__)

# celery -A app.routes.task_management.celery worker --loglevel=info --concurrency=1 -Q unittest_generation
celery.conf.update(
    task_default_queue='unittest_generation',
    task_routes={'app.routes.task_management.generate_unittest_task': {'queue': 'unittest_generation'}},
    worker_prefetch_multiplier=1,
    worker_concurrency=1,
)


@celery.task(bind=True)
def generate_unittest_task(self, file_path, task_id):
    try:
        os.makedirs(os.makedirs(current_app.config['DOWNLOAD_FOLDER']))
        with open(file_path, 'r') as file:
            code = file.read()
        all_tests = model_manager.generate_unittest(code)
        output_path = os.path.join(current_app.config['DOWNLOAD_FOLDER'], f"{task_id}_unittest.py")
        with open(output_path, 'w') as file:
            for test in all_tests:
                file.write(test.model_dump_json() + '\n')
        return {'status': 'completed', 'output_path': output_path}
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}
import pdb
@task_management_bp.route('/upload', methods=['POST'])
def upload_file():
    os.makedirs(current_app.config['UPLOAD_FOLDER'])
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        task_id = str(uuid.uuid4())
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"{task_id}_{filename}")
        file.save(file_path)
        task = generate_unittest_task.delay(file_path, task_id)
        return jsonify({'task_id': task_id, 'status': 'processing'}), 202


@task_management_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = generate_unittest_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'status': 'processing'}
    elif task.state != 'FAILURE':
        response = task.info
    else:
        response = {'status': 'failed', 'error': str(task.info)}
    return jsonify(response)

@task_management_bp.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    file_path = os.path.join(tempfile.gettempdir(), f"{task_id}_unittest.py")
    return send_file(file_path, as_attachment=True)

from celery.app.control import Inspect

@task_management_bp.route('/queue_status', methods=['GET'])
def get_queue_status():
    inspect = celery.control.inspect()
    active = inspect.active()
    reserved = inspect.reserved()
    
    if active is not None and reserved is not None:
        active_count = sum(len(tasks) for tasks in active.values())
        reserved_count = sum(len(tasks) for tasks in reserved.values())
        return jsonify({
            'active_tasks': active_count,
            'queued_tasks': reserved_count
        })
    return jsonify({'error': 'Could not retrieve queue status'}), 500