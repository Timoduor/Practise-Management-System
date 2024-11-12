from django.contrib import admin
from hub.models.sales_type import SalesType

@admin.register(SalesType)
class SalesTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)
