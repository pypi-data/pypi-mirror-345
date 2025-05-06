# -*- coding: UTF-8 -*-
from celery import states

from kyutil.http_util import send_request


def celery_state_update(celery_status_func, logger_, msg, percent, status, task_id, **kwargs):
    """
    celery实时状态更新以及信息回传更新
    celery_status celery类内更新函数
    status 函数状态
    """
    process_percent = str(percent)
    msg = msg.decode(encoding='utf-8', errors='ignore') if isinstance(msg, bytes) else str(msg)
    if msg.strip():
        logger_.info(f"Celery进度更新: {task_id[:4]} >> {msg}")
        data_ = {'current': process_percent, 'message': msg, "status": status, **kwargs}
        if celery_status_func is not None:
            # 异常抛出状态
            if status is False:
                celery_status_func(state=states.FAILURE, meta=data_, task_id=task_id)
            # 执行完成状态
            elif percent == 100:
                celery_status_func(state=states.SUCCESS, meta=data_, task_id=task_id)
            # 其他状态，代表执行中
            else:
                celery_status_func(state=states.STARTED, meta=data_, task_id=task_id)


def get_dashboard(domain="localhost"):
    """
    获取flower的json
    Args:
        domain:

    Returns:

    """
    url = f"{domain}/dashboard?json=1"
    res = send_request(url, timeout=4)
    return res.json()
