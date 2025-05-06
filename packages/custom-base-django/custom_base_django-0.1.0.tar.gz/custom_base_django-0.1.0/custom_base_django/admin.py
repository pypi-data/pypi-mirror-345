from django.contrib import admin
from .models.periodict_tasks import PeriodicTasks, RunPeriodicTasks
# Register your models here.


admin.site.register([PeriodicTasks, RunPeriodicTasks])