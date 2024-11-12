from django.contrib import admin
from hub.models.sales_task_status import SalesTaskStatus

@admin.register(SalesTaskStatus)
class SalesTaskStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
