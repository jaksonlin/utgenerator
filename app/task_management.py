import logging
import os
import pdb
import tempfile
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from .tasks import get_celery_stat
from .tasks import hello_world_task, generate_unittest_task
task_management_bp = Blueprint('task_management', __name__)


@task_management_bp.route('/hello', methods=['GET'])
def hello():
    task_id = str(uuid.uuid4())
    task = hello_world_task.delay(task_id)
    return jsonify({'task_id': task_id, 'status': 'processing'}), 200

@task_management_bp.route('/upload', methods=['POST'])
def upload_file():
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
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

@task_management_bp.route('/queue_status', methods=['GET'])
def get_queue_status():
    result = get_celery_stat()
    if result is not None:
        return jsonify(result)
    return jsonify({'error': 'Could not retrieve queue status'}), 500