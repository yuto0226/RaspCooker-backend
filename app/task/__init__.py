# -*- encoding: utf-8 -*-
from queue import Queue
import threading
import time
import subprocess
from datetime import datetime
from flask import Blueprint
import logging
from typing import Dict, Any

# 常數定義
TASK_TIMEOUT_SECONDS = 1800  # 30 分鐘
SCHEDULER_SLEEP_INTERVAL = 0.1

# 日誌設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Blueprint 註冊
blueprint = Blueprint('task', __name__)

# 全域變數
tasks: Dict[str, Dict[str, Any]] = {}
task_queue = Queue()

def update_task_state(task_uuid: str, state: str, **kwargs) -> None:
    """更新指定任務的狀態"""
    if task_uuid not in tasks:
        logger.error(f"Task {task_uuid} not found for state update")
        return

    tasks[task_uuid].update({'state': state, **kwargs})
    logger.info(f"Task {task_uuid} updated to state '{state}'")

def execute_task(task_info: Dict[str, Any]) -> None:
    """執行指定的任務"""
    task_uuid = task_info['uuid']
    file_path = task_info['file_path']

    try:
        update_task_state(task_uuid, 'RUNNING', start_time=datetime.now().isoformat())
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
                'TERMINATED',
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
                'TERMINATED',
                term_time=datetime.now().isoformat()
            )
            logger.error(f"Task {task_uuid} timed out")

    except Exception as e:
        logger.error(f"Error executing task {task_uuid}: {str(e)}")
        update_task_state(
            task_uuid,
            'TERMINATED',
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

        current_state = tasks[task_uuid]['state']
        if current_state not in ['WAITING', 'RUNABLE']:
            logger.warning(f"Task {task_uuid} skipped: Invalid state '{current_state}'")
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

# 啟動排程器
def start_scheduler() -> None:
    """啟動排程器執行緒"""
    scheduler_thread = threading.Thread(target=task_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Task scheduler started")

start_scheduler()
