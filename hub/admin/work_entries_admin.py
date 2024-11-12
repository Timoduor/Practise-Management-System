from django.contrib import admin
from hub.models.work_entries import WorkEntries

@admin.register(WorkEntries)
class WorkEntriesAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Work Info", {"fields": ["date", "start_time", "end_time", "description", "task_type"]}),
        ("Task", {"fields": ["project", "phase", "task"]}),
        ("User", {"fields": ["user"]}),
    ]
    list_display = ('user', 'date', 'start_time', 'end_time', 'task_type', 'project', 'phase', 'task', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name', 'phase__phase_name', 'task__task_name')
    list_filter = ('task_type', 'project', 'phase', 'date', 'is_deleted')
