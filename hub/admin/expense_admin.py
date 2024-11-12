from django.contrib import admin
from hub.models.expense import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Expense Info", {"fields": ["value", "date", "description"]}),
        ("Project Info", {"fields": ["project", "phase", "task"]}),
        ("User", {"fields": ["user"]}),
    ]
    list_display = ('user', 'project', 'phase', 'task', 'value', 'date', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name', 'phase__phase_name', 'task__task_name')
    list_filter = ('date', 'project', 'phase', 'task', 'is_deleted')
