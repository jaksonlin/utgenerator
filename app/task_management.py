import os
import uuid
import io
from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
from .tasks import hello_world_task, generate_unittest_task_from_redis
from .redis_svc import get_current_task_status, add_task_to_redis, get_task_result, get_tasks_by_page, get_task_status
from .task_status import *

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
    
    filename = secure_filename(file.filename)
    file_content = file.read().decode('utf-8')
    task = add_task_to_redis(filename=filename, file_content=file_content)
    generate_unittest_task_from_redis.delay(task['task_id'])
    return jsonify(task), 202
    
@task_management_bp.route('/task/<task_id>', methods=['GET'])
def get_task_status(task_id):
    task = get_task_status(task_id=task_id)
    return jsonify(task), 200

@task_management_bp.route('/download/<task_id>', methods=['GET'])
def download_file(task_id):
    filename, file_content= get_task_result(task_id)
    if not filename:
        return jsonify({'error': 'File not found'}), 404
    return send_file(
        io.BytesIO(file_content),
        mimetype='application/octet-stream',
        as_attachment=True,
        attachment_filename=filename
    )
    
@task_management_bp.route('/tasks', methods=['GET'])
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    tasks_data = get_tasks_by_page(page, per_page)
    return jsonify(tasks_data), 200

@task_management_bp.route('/queue_status', methods=['GET'])
def queue_status():
    try:
        # Get status counts
        status_counts = get_current_task_status()
        total = sum(status_counts.values())
        
        return jsonify({
            'total_tasks': total,
            'active_tasks': status_counts.get(TASK_RUN, 0),
            'queued_tasks': status_counts.get(TASK_INIT, 0),
            'completed_tasks': status_counts.get(TASK_SUCC, 0),
            'failed_tasks': status_counts.get(TASK_FAIL, 0),
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'An error occurred while fetching queue status: {str(e)}'
        }), 500