from django.contrib import admin
from hub.models.task_type import TaskType

@admin.register(TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
