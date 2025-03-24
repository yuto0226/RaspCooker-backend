import os
import uuid
from datetime import datetime
from flask import jsonify
from app.task import blueprint, tasks, task_queue
from app.auth import token_required
from app.file import uploads_dir
from typing import Dict, Any

def initialize_task(file_name: str, file_path: str) -> Dict[str, Any]:
    """初始化任務並加入全域任務列表"""
    task_uuid = str(uuid.uuid4())
    task_data = {
        'uuid': task_uuid,
        'file_name': file_name,
        'file_path': file_path,
        'state': 'CREATED',
        'return_code': None,
        'stdout': "",
        'stderr': "",
        'start_time': datetime.now().isoformat(),
        'term_time': None
    }
    tasks[task_uuid] = task_data
    return task_data

def enqueue_task(task_uuid: str, file_path: str) -> None:
    """將任務加入佇列並更新狀態"""
    task_queue.put({
        'uuid': task_uuid,
        'file_path': file_path
    })
    tasks[task_uuid]['state'] = 'RUNABLE'

@blueprint.route('/')
@token_required
def list_tasks():
    """列出所有任務"""
    task_list = [
        {
            'uuid': task_uuid,
            'file_name': task_info.get('file_name'),
            'file_path': task_info.get('file_path'),
            'state': task_info.get('state'),
            'start_time': task_info.get('start_time'),
            'term_time': task_info.get('term_time')
        }
        for task_uuid, task_info in tasks.items()
    ]
    return jsonify({
        'tasks': task_list,
        'total': len(task_list)
    })

@blueprint.route('/<task_uuid>')
@token_required
def task_info(task_uuid: str):
    """取得指定任務的詳細資訊"""
    if task_uuid not in tasks:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({
        'tasks': tasks[task_uuid],
        'total': 1
    })

@blueprint.route('/<file_name>/run', methods=['POST'])
@token_required
def create_task(file_name: str):
    """建立並執行新任務"""
    file_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    task_data = initialize_task(file_name, file_path)
    enqueue_task(task_data['uuid'], file_path)

    return jsonify({
        "message": "Task queued successfully",
        "task_uuid": task_data['uuid']
    }), 200
