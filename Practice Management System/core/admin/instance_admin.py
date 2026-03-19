from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from core.models.instance import Instance
from .base_admin import SoftDeleteAdmin, JurisdictionInline

@admin.register(Instance)
class InstanceAdmin(SoftDeleteAdmin):
    list_display = (
        'get_instance_name',
        'get_industry_sector',
        'get_status',
        'get_entities_count',
        'DateAdded',
    )

    search_fields = (
        'instanceName',
        'industrySector__industryTitle',
        'industrySector__industryCategory',
    )

    list_filter = (
        'is_deleted',
        'Lapsed',
        'Suspended',
        'industrySector',
        'DateAdded',
    )

    autocomplete_fields = ['industrySector']

    readonly_fields = (
        'instanceID',
        'DateAdded',
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Instance Information', {
            'fields': (
                'instanceName',
                'industrySector',
            )
        }),
        ('Status', {
            'fields': (
                'Lapsed',
                'Suspended',
                'is_deleted',
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'instanceID',
                'DateAdded',
                'created_at',
                'created_by',
                'updated_at',
                'last_updated_by',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [JurisdictionInline]

    def get_instance_name(self, obj):
        """Display instance name with status indicators"""
        status_icons = []
        if obj.Lapsed:
            status_icons.append('🕒')  # Clock for lapsed
        if obj.Suspended:
            status_icons.append('⏸️')  # Pause for suspended
        if obj.is_deleted:
            status_icons.append('🗑️')  # Trash for deleted
        
        status_str = ' '.join(status_icons)
        return format_html(
            '<strong>{}</strong> {}',
            obj.instanceName,
            status_str
        )
    get_instance_name.short_description = 'Instance Name'
    get_instance_name.admin_order_field = 'instanceName'

    def get_industry_sector(self, obj):
        """Display industry sector with category"""
        if obj.industrySector:
            return format_html(
                '<span title="Category: {}">{}</span>',
                obj.industrySector.industryCategory,
                obj.industrySector.industryTitle
            )
        return '-'
    get_industry_sector.short_description = 'Industry Sector'
    get_industry_sector.admin_order_field = 'industrySector__industryTitle'

    def get_status(self, obj):
        """Display status with color indicators"""
        statuses = []
        if obj.is_deleted:
            statuses.append(format_html('<span style="color: red;">Deleted</span>'))
        if obj.Suspended:
            statuses.append(format_html('<span style="color: orange;">Suspended</span>'))
        if obj.Lapsed:
            statuses.append(format_html('<span style="color: yellow;">Lapsed</span>'))
        if not statuses:
            return format_html('<span style="color: green;">Active</span>')
        return format_html(' | '.join(statuses))
    get_status.short_description = 'Status'

    def get_entities_count(self, obj):
        """Display count of entities in this instance"""
        count = obj.entities.count()
        return format_html(
            '<span class="entity-count">{}</span>',
            count
        )
    get_entities_count.short_description = 'Entities'
    get_entities_count.admin_order_field = 'entities__count'

    def get_queryset(self, request):
        """Optimize queryset with annotations and related fields"""
        return super().get_queryset(request).select_related(
            'industrySector'
        ).annotate(
            models.Count('entities', distinct=True)
        )

    def save_model(self, request, obj, form, change):
        """Track who created/updated the instance"""
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/instance_admin.css',)
        }
        js = ('admin/js/instance_admin.js',)