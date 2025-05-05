from django.contrib import admin
from django.utils.html import format_html
from core.models.industry_sector import IndustrySector
from .base_admin import SoftDeleteAdmin
from django.db import models

@admin.register(IndustrySector)
class IndustrySectorAdmin(SoftDeleteAdmin):
    list_display = (
        'get_industry_title',
        'industryCategory',
        'get_status',
        'get_entities_count',
        'DateAdded',
        'get_last_updated',
    )

    search_fields = (
        'industryTitle',
        'industryCategory',
        'LastUpdatedByID__email',
        'LastUpdatedByID__firstName',
        'LastUpdatedByID__surname',
    )

    list_filter = (
        'Suspended',
        'industryCategory',
        'DateAdded',
    )

    readonly_fields = (
        'industrySectorID',
        'DateAdded',
        'LastUpdatedByID',
    )

    fieldsets = (
        ('Industry Information', {
            'fields': (
                'industryTitle',
                'industryCategory',
            )
        }),
        ('Status', {
            'fields': (
                'Suspended',
            ),
        }),
        ('System Information', {
            'fields': (
                'industrySectorID',
                'DateAdded',
                'LastUpdatedByID',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_industry_title(self, obj):
        """Display industry title with category tooltip"""
        return format_html(
            '<strong title="Category: {}">{}</strong>',
            obj.industryCategory,
            obj.industryTitle
        )
    get_industry_title.short_description = 'Industry'
    get_industry_title.admin_order_field = 'industryTitle'

    def get_status(self, obj):
        """Display status with color indicator"""
        if obj.Suspended == 'N':
            return format_html(
                '<span style="color: green;">●</span> Active'
            )
        return format_html(
            '<span style="color: red;">●</span> Suspended'
        )
    get_status.short_description = 'Status'
    get_status.admin_order_field = 'Suspended'

    def get_entities_count(self, obj):
        """Display count of entities in this sector"""
        count = obj.entities.count()
        return format_html(
            '<span class="entity-count">{}</span>',
            count
        )
    get_entities_count.short_description = 'Entities'
    get_entities_count.admin_order_field = 'entities__count'

    def get_last_updated(self, obj):
        """Display last update info with user"""
        if obj.LastUpdatedByID:
            return format_html(
                'By {} {}',
                obj.LastUpdatedByID.firstName,
                obj.LastUpdatedByID.surname
            )
        return '-'
    get_last_updated.short_description = 'Last Updated By'
    get_last_updated.admin_order_field = 'LastUpdatedByID'

    def save_model(self, request, obj, form, change):
        """Set the last updated by user"""
        obj.LastUpdatedByID = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimize queryset with annotations and related fields"""
        return super().get_queryset(request).select_related(
            'LastUpdatedByID'
        ).annotate(
            models.Count('entities', distinct=True)
        )

    class Media:
        css = {
            'all': ('admin/css/industry_sector_admin.css',)
        }
        js = ('admin/js/industry_sector_admin.js',)