# -*- coding: UTF-8 -*-
from celery import states
from retry import retry


@retry(delay=0.2, tries=5)
def get_active_task(celery_app):
    return celery_app.control.inspect().active()


@retry(delay=0.2, tries=5)
def get_active_queues(celery_app):
    return celery_app.control.inspect().active_queues()


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
