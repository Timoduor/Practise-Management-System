from django.contrib import admin
from hub.models.sales_task_type import SalesTaskType

@admin.register(SalesTaskType)
class SalesTaskTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
