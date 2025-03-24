# -*- encoding: utf-8 -*-
from queue import Queue
import threading
import time
import subprocess
from datetime import datetime
from flask import Blueprint
import logging
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

# 常數定義
TASK_TIMEOUT_SECONDS = 1800  # 30 分鐘
SCHEDULER_SLEEP_INTERVAL = 0.1

class TaskState(Enum):
    CREATED = "CREATED"
    WAITING = "WAITING"
    RUNABLE = "RUNABLE"
    RUNNING = "RUNNING"
    TERMINATED = "TERMINATED"

@dataclass
class Task:
    uuid: str
    file_path: str
    state: TaskState
    start_time: Optional[str] = None
    term_time: Optional[str] = None
    return_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None

# 日誌設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Blueprint 註冊
blueprint = Blueprint('task', __name__)

# 全域變數
tasks: Dict[str, Task] = {}
task_queue = Queue()

def update_task_state(task_uuid: str, state: TaskState, **kwargs) -> None:
    """更新指定任務的狀態"""
    if task_uuid not in tasks:
        logger.error(f"Task {task_uuid} not found for state update")
        return

    task = tasks[task_uuid]
    task.state = state
    for key, value in kwargs.items():
        setattr(task, key, value)

    logger.info(f"Task {task_uuid} updated to state '{state.value}'")

def execute_task(task_info: Dict[str, Any]) -> None:
    """執行指定的任務"""
    task_uuid = task_info['uuid']
    file_path = task_info['file_path']

    try:
        update_task_state(task_uuid, TaskState.RUNNING, start_time=datetime.now().isoformat())
        logger.info(f"Starting task {task_uuid} with file {file_path}")

        process = subprocess.Popen(
            ['python', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        try:
            stdout, stderr = process.communicate(timeout=TASK_TIMEOUT_SECONDS)
            update_task_state(
                task_uuid,
                TaskState.TERMINATED,
                return_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
                term_time=datetime.now().isoformat()
            )
            logger.info(f"Task {task_uuid} completed with return code {process.returncode}")

        except subprocess.TimeoutExpired:
            process.kill()
            update_task_state(
                task_uuid,
                TaskState.TERMINATED,
                term_time=datetime.now().isoformat()
            )
            logger.error(f"Task {task_uuid} timed out")

    except Exception as e:
        logger.error(f"Error executing task {task_uuid}: {str(e)}")
        update_task_state(
            task_uuid,
            TaskState.TERMINATED,
            term_time=datetime.now().isoformat()
        )

def process_task_queue() -> None:
    """處理任務佇列中的任務"""
    while not task_queue.empty():
        task_info = task_queue.get()
        task_uuid = task_info['uuid']

        if task_uuid not in tasks:
            logger.error(f"Task {task_uuid} not found in task list")
            continue

        task = tasks[task_uuid]
        if task.state not in {TaskState.WAITING, TaskState.RUNABLE}:
            logger.warning(f"Task {task.uuid} skipped: Invalid state '{task.state.value}'")
            continue

        logger.info(f"Scheduler picked up task {task_uuid}")
        execute_task(task_info)

def task_scheduler() -> None:
    """任務排程器主迴圈"""
    while True:
        try:
            process_task_queue()
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
        time.sleep(SCHEDULER_SLEEP_INTERVAL)

def start_scheduler() -> None:
    """啟動排程器執行緒"""
    scheduler_thread = threading.Thread(target=task_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Task scheduler started")

def add_task(uuid: str, file_path: str) -> None:
    """新增任務到佇列"""
    task = Task(uuid=uuid, file_path=file_path, state=TaskState.WAITING)
    tasks[uuid] = task
    task_queue.put({"uuid": uuid, "file_path": file_path})
    logger.info(f"Task {uuid} added to queue with state '{task.state.value}'")

start_scheduler()
