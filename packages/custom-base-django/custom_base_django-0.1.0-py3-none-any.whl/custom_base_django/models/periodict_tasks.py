from .base import BaseModelFiscalDelete, BaseModelWitDateNotFiscalDelete
from django.db import models
from .choices import *



class PeriodicTasks(BaseModelWitDateNotFiscalDelete):
    functions = models.JSONField(verbose_name="Functions", default=['func1'])
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    # period_choice = ChoiceForeignKey(limit_title="period_choice", related_name="period_choice", verbose_name="period_choice")
    # period_choice_params = models.JSONField(verbose_name="period_choice_params", help_text={"interval_num": 1, "interval_period": "hours"})
    # is_active = models.BooleanField(verbose_name="is_active", default=True)
    run_parallel = models.BooleanField(verbose_name="run_parallel", default=True)

    # start_time = models.DateTimeField(verbose_name="start_time", null=True, blank=True)
    # end_time = models.DateTimeField(verbose_name="end_time", null=True, blank=True)
    # args = models.JSONField(verbose_name="args", null=True, blank=True)
    # kwargs = models.JSONField(verbose_name="kwargs", null=True, blank=True)

    @property
    def mean_duration(self):
        runs = self.runs.filter(status_id=36).order_by('-id')[:10]
        m_sum = 0
        for run in runs:
            m_sum += (run.end_time - run.start_time).total_seconds()
        return m_sum / len(runs) if len(runs) else 4000


class RunPeriodicTasks(BaseModelFiscalDelete):
    task = models.ForeignKey(PeriodicTasks, related_name="runs", verbose_name="task", on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name="start_time")
    end_time = models.DateTimeField(auto_now=True, blank=True, null=True, verbose_name="end_time")
    status = ChoiceForeignKey(limit_title="task_status", related_name="task_status", verbose_name="task_status")
    res = models.JSONField(verbose_name="res", null=True, blank=True)


