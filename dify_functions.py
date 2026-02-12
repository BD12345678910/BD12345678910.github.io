from wsgiref import headers
import requests
import json
from typing import Dict, Any
import time
from sql_functions_v3 import SQLManager as sql_functions
from logger import logger
from celery import Celery
app = Celery('tasks', broker='redis://localhost:6379/0')

# 限制Worker并发数为5
app.conf.worker_concurrency = 5

api_key = "app-E5mnWlXIOEKgaIJdlecPoKYr"
url = "http://localhost/v1/chat-messages"

@app.task
def call_dify_workflow(
    stu_id: int,
    teacher_id: int,
    class_id: int,
    prompt: str,
    user_id: str,
    base_url: str = "http://localhost/v1/chat-messages",
    conversation_id: str = '',
    subject: str = ''
) -> str: 
    '''调用Dify工作流接口'''
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "user": user_id,
        "query": prompt,
        "response_mode": "blocking", 
        "inputs": {'query_subject':subject}, 
        "conversation_id": conversation_id, 
        "files": [{}]
    }
    try:
        response = requests.post(
            url=base_url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()

        response_data = response.json()
        workflow_output = response_data["answer"]
        
        sql_functions.add_query(stu_id,teacher_id,class_id,prompt,workflow_output)
        return workflow_output

    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {str(e)}")
    except KeyError:
        logger.error("响应格式错误，缺少预期的键")

print(call_dify_workflow(0,0,0,'what is AI?','test_user','http://localhost/v1/chat-messages','' ,''))



