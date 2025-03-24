import os
import uuid
from datetime import datetime
from flask import jsonify, request
from app.task import blueprint, tasks, add_task, TaskState, Task, update_task_state
from app.auth import token_required
from app.file import uploads_dir
from typing import Dict

def initialize_task(file_name: str, file_path: str) -> Task:
    """初始化任務並加入全域任務列表"""
    task_uuid = str(uuid.uuid4())
    task = Task(
        uuid=task_uuid,
        file_path=file_path,
        state=TaskState.CREATED,
        start_time=datetime.now().isoformat()
    )
    tasks[task_uuid] = task
    return task

@blueprint.route('/')
@token_required
def list_tasks():
    """列出所有任務"""
    task_list = [
        {
            'uuid': task.uuid,
            'file_path': task.file_path,
            'state': task.state.value,
            'start_time': task.start_time,
            'term_time': task.term_time
        }
        for task in tasks.values()
    ]
    return jsonify({
        'tasks': task_list,
        'total': len(task_list)
    })

@blueprint.route('/<task_uuid>')
@token_required
def task_info(task_uuid: str):
    """取得指定任務的詳細資訊"""
    task = tasks.get(task_uuid)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        'uuid': task.uuid,
        'file_path': task.file_path,
        'state': task.state.value,
        'start_time': task.start_time,
        'term_time': task.term_time,
        'return_code': task.return_code,
        'stdout': task.stdout,
        'stderr': task.stderr
    })

@blueprint.route('/<file_name>/run', methods=['POST'])
@token_required
def create_task(file_name: str):
    """建立並執行新任務"""
    file_path = os.path.join(uploads_dir, file_name)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404

    task_uuid = str(uuid.uuid4())
    task = Task(
        uuid=task_uuid,
        file_path=file_path,
        state=TaskState.WAITING
    )
    tasks[task_uuid] = task
    add_task(task_uuid, file_path)

    return jsonify({
        "message": "Task queued successfully",
        "task_uuid": task_uuid
    }), 200
