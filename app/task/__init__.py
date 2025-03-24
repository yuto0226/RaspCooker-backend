# -*- encoding: utf-8 -*-
from queue import Queue
import threading
import time
import subprocess
from datetime import datetime
from flask import Blueprint
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

blueprint = Blueprint(
    'task',
    __name__,
)

"""
tasks[uuid] = {
    'file_path': str,    # 檔案完整路徑
    'file_name': str,    # 檔案名稱
    'state': str,        # CREATED/RUNNING/TERMINATED/FAILED
    'return_code': int,  # 程式執行回傳值
    'stdout': str,       # 標準輸出
    'stderr': str,       # 錯誤輸出
    'start_time': str,   # ISO格式的開始時間
    'term_time': str,    # ISO格式的結束時間
    'error': str        # 如果執行失敗，記錄錯誤訊息
}
"""
tasks = {}
task_queue = Queue()

def execute_task(task_info):
    task_uuid = task_info['uuid']
    file_path = task_info['file_path']
    
    try:
        # 更新開始執行狀態
        tasks[task_uuid].update({
            'state': 'RUNNING',
            'start_time': datetime.now().isoformat()
        })
        logger.info(f"Starting task {task_uuid} with file {file_path}")
        
        # 執行程式
        process = subprocess.Popen(
            ['python', file_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=1800)
            
            tasks[task_uuid].update({
                'state': 'TERMINATED',
                'return_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'term_time': datetime.now().isoformat()
            })
            
        except subprocess.TimeoutExpired:
            process.kill()
            tasks[task_uuid].update({
                'state': 'TERMINATED',
                'term_time': datetime.now().isoformat()
            })
            logger.error(f"Task {task_uuid} timed out")
            
    except Exception as e:
        # 處理其他可能的錯誤
        error_msg = str(e)
        tasks[task_uuid].update({
            'state': 'TERMINATED',
            'term_time': datetime.now().isoformat()
        })
        logger.error(f"Error executing task {task_uuid}: {error_msg}")
        
    finally:
        # 確保任務一定有結束時間
        if 'term_time' not in tasks[task_uuid]:
            tasks[task_uuid]['term_time'] = datetime.now().isoformat()

def task_scheduler():
    while True:
        try:
            if not task_queue.empty():
                task_info = task_queue.get()
                logger.info(f"Scheduler picked up task {task_info['uuid']}")
                execute_task(task_info)
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            continue

# 啟動排程器
scheduler_thread = threading.Thread(target=task_scheduler, daemon=True)
scheduler_thread.start()
logger.info("Task scheduler started")
