# tasks.py (در اپلیکیشن مربوطه)
from celery import shared_task
from datetime import datetime
from django.utils import timezone

from conf.celery import app
from .models.periodict_tasks import PeriodicTasks, RunPeriodicTasks
from django.core.cache import cache
import importlib


# def test_task(res=None,*args, **kwargs):
#     print('test')
#     print(f"{res}, {args}, {kwargs}")
#     return res

@shared_task
def execute_periodic_task(*args, **kwargs):
    # گرفتن تسک از مدل PeriodicTasks
    task = PeriodicTasks.objects.filter(id=kwargs.get('task_id', 0)).first()

    if not task:
        return {"error": "undefined task"}

    # ذخیره وضعیت شروع تسک
    run_task = RunPeriodicTasks(task=task, status_id=35)#start
    run_task.save()
    if not kwargs.get('force') and not task.run_parallel and cache.get(f'run_task-{task.id}'):
        res = {"error": "task is running" }
        return res

    cache.set(f'run_task-{task.id}', True, task.mean_duration)
    try:
        res = {}
        for function in task.functions:
            module_name, function_name = function.rsplit('.', 1)
            module = importlib.import_module(module_name)
            function = getattr(module, function_name, None)
            if function:
                res = function(res=res, *args, **kwargs)
        # ذخیره نتیجه و وضعیت پایان تسک
        # run_task.end_time = timezone.now()
        run_task.status_id = 36#'Completed'
        run_task.res = res
        return res or {}
    except Exception as e:
        # در صورت بروز خطا، ذخیره وضعیت شکست تسک
        # run_task.end_time = timezone.now()
        run_task.status_id = 37#'Failed'
        res = {"error": str(e)}
        return res
    finally:
        cache.set(f'run_task-{task.id}', False, 100)
        run_task.save()