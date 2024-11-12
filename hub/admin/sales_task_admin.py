from django.contrib import admin
from hub.models.sales_task import SalesTask

@admin.register(SalesTask)
class SalesTaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'sale', 'assigned_to', 'date', 'task_status', 'created_at', 'updated_at')
    search_fields = ('task_name', 'sale__sales_name', 'assigned_to__email')
    list_filter = ('task_status', 'date', 'is_deleted')
