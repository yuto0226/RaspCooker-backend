import os
import uuid
import subprocess
import threading
from datetime import datetime
from flask import jsonify
from app.task import blueprint, tasks, task_queue
from app.auth import token_required
from app.file import uploads_dir

"""
list all tasks records' uuid
"""
@blueprint.route('/')
@token_required
def list_tasks():
    task_list = []
    for task_uuid, task_info in tasks.items():
        task_list.append({
            'uuid': task_uuid,
            'file_name': task_info.get('file_name'),
            'state': task_info.get('state'),
            'start_time': task_info.get('start_time'),
            'term_time': task_info.get('term_time')
        })
    
    return jsonify({
        'tasks': task_list,
        'total': len(task_list)
    })
    
@blueprint.route('/<task_uuid>')
@token_required
def task_info(task_uuid):
    if task_uuid not in tasks:
        return jsonify({"error": "Task not found"}), 404
        
    return jsonify({
        'tasks': tasks[task_uuid],
        'total': 1
    })

@blueprint.route('/<file_name>/run', methods=['POST'])
@token_required
def create_task(file_name):
    file_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    task_uuid = str(uuid.uuid4())
    
    # 建立任務資訊但不立即執行
    tasks[task_uuid] = {
        'file_path': file_path,
        'file_name': file_name,
        'state': 'CREATED',
        'return_code': None,
        'stdout': "",
        'stderr': "",
        'start_time': datetime.now().isoformat(),
        'term_time': None
    }

    # 將任務加入佇列
    task_queue.put({
        'uuid': task_uuid,
        'file_path': file_path
    })

    return jsonify({
        "message": "Task queued successfully", 
        "task_uuid": task_uuid
    }), 200
