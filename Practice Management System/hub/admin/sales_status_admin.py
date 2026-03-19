from django.contrib import admin
from hub.models.sales_status import SalesStatus

@admin.register(SalesStatus)
class SalesStatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
