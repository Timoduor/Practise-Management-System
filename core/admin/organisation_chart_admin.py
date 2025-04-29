from django.contrib import admin
from core.models.organisation_chart import OrganisationChart
from .base_admin import BaseModelAdmin
from django.utils.html import format_html


@admin.register(OrganisationChart)
class OrganisationChartAdmin(BaseModelAdmin):
    """Admin interface for OrganisationChart model"""
    
    list_display = [
        'orgChartID',
        'orgChartName',
        'entity_link',
        'DateAdded',
        'LastUpdate',
        'updated_by',
        'status_badge',
    ]

    list_filter = [
        'entityID',
        'Suspended',
        'Lapsed',
        'DateAdded',
        'LastUpdate',
    ]

    search_fields = [
        'orgChartID',
        'orgChartName',
        'entityID__name',  # Assuming entity has a name field
        'LastUpdatedByID__email',  # Search by user email
    ]

    readonly_fields = [
        'orgChartID',
        'DateAdded',
        'LastUpdate',
        'created_by',
        'last_updated_by',
    ]

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'orgChartName',
                'entityID',
                'orgDataID',
            )
        }),
        ('Status', {
            'fields': (
                'Suspended',
                'Lapsed',
            )
        }),
        ('Audit Information', {
            'fields': (
                'orgChartID',
                'DateAdded',
                'LastUpdate',
                'LastUpdatedByID',
            ),
            'classes': ('collapse',)
        }),
    )

    def entity_link(self, obj):
        """Create a clickable link to the entity"""
        if obj.entityID:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/core/entity/{obj.entityID.id}/change/',
                str(obj.entityID)
            )
        return "-"
    entity_link.short_description = 'Entity'
    entity_link.admin_order_field = 'entityID__name'

    def updated_by(self, obj):
        """Display user who last updated the record"""
        if obj.LastUpdatedByID:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/core/user/{obj.LastUpdatedByID.id}/change/',
                obj.LastUpdatedByID.email
            )
        return "-"
    updated_by.short_description = 'Last Updated By'
    updated_by.admin_order_field = 'LastUpdatedByID__email'

    def status_badge(self, obj):
        """Display status as a colored badge"""
        status = obj.status
        colors = {
            'Active': 'green',
            'Suspended': 'red',
            'Lapsed': 'orange'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px;">{}</span>',
            colors.get(status, 'gray'),
            status
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        """Override save_model to handle user tracking"""
        if not change:  # New object
            obj.created_by = request.user
        obj.LastUpdatedByID = request.user
        super().save_model(request, obj, form, change)

    # Custom actions
    actions = ['suspend_charts', 'unsuspend_charts', 'lapse_charts', 'unlapse_charts']

    def suspend_charts(self, request, queryset):
        """Bulk suspend selected charts"""
        updated = queryset.update(Suspended='Y')
        self.message_user(request, f'{updated} charts were suspended.')
    suspend_charts.short_description = 'Suspend selected charts'

    def unsuspend_charts(self, request, queryset):
        """Bulk unsuspend selected charts"""
        updated = queryset.update(Suspended='N')
        self.message_user(request, f'{updated} charts were unsuspended.')
    unsuspend_charts.short_description = 'Unsuspend selected charts'

    def lapse_charts(self, request, queryset):
        """Bulk lapse selected charts"""
        updated = queryset.update(Lapsed='Y')
        self.message_user(request, f'{updated} charts were marked as lapsed.')
    lapse_charts.short_description = 'Mark selected charts as lapsed'

    def unlapse_charts(self, request, queryset):
        """Bulk unlapse selected charts"""
        updated = queryset.update(Lapsed='N')
        self.message_user(request, f'{updated} charts were unmarked as lapsed.')
    unlapse_charts.short_description = 'Unmark selected charts as lapsed'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }