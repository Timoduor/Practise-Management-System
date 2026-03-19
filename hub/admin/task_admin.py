from django.contrib import admin
from hub.models.task import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Task Info", {"fields": ["task_name", "task_description", "start_date", "due_date", "task_type", "task_status"]}),
        ("Phase", {"fields": ["phase"]}),
        ("Assigned To", {"fields": ["assigned_to"]}),
    ]
    list_display = ('task_name', 'get_phase_name', 'assigned_to', 'start_date', 'due_date', 'task_status', 'created_at', 'task_type', 'updated_at')
    search_fields = ('task_name', 'phase__phase_name', 'assigned_to__email')
    list_filter = ('task_status', 'start_date', 'due_date', 'is_deleted')

    def get_phase_name(self, obj):
        return obj.phase.phase_name
    get_phase_name.short_description = 'Phase Name'
