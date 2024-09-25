import os
import uuid
import io
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from .tasks import get_celery_stat
from .tasks import hello_world_task, generate_unittest_task_from_redis
from .redis_svc import redis_client
from celery.exceptions import TimeoutError

task_management_bp = Blueprint('task_management', __name__)


@task_management_bp.route('/hello', methods=['GET'])
def hello():
    task_id = str(uuid.uuid4())
    hello_world_task.delay(task_id)
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
        file_content = file.read().decode('utf-8')
        file_extension = os.path.splitext(filename)[1]
        task_id = str(uuid.uuid4())
        # Store file info and content in a hash
        redis_client.hset(task_id, mapping={
            'content': file_content,
            'extension': file_extension,
            'original_filename': filename
        })
        task = generate_unittest_task_from_redis.delay(task_id)
        return jsonify({'task_id': task_id, 'status': 'processing'}), 202


@task_management_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = generate_unittest_task_from_redis.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'status': 'processing'}
    elif task.state != 'FAILURE':
        response = task.info
    else:
        response = {'status': 'failed', 'error': str(task.info)}
    return jsonify(response)

@task_management_bp.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    file_info = redis_client.hgetall(f'rs-{task_id}')
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
    
    file_content = file_info[b'content']
    file_extension = file_info[b'extension'].decode('utf-8')
    original_filename = file_info[b'original_filename'].decode('utf-8')
    
    return send_file(
        io.BytesIO(file_content),
        mimetype='application/octet-stream',
        as_attachment=True,
        attachment_filename=f"{original_filename}_unittest.{file_extension}"
    )

@task_management_bp.route('/queue_status', methods=['GET'])
def queue_status():
    celery_stat = get_celery_stat()
    if celery_stat['status'] == 'available':
        return jsonify(celery_stat), 200
    elif celery_stat['status'] == 'partially_available':
        return jsonify(celery_stat), 206  # Partial Content
    elif celery_stat['status'] == 'timeout':
        return jsonify(celery_stat), 503  # Service Unavailable
    else:
        return jsonify(celery_stat), 500  