from django.contrib import admin
from core.models.organisation_chart_position_assignment import OrganisationChartPositionAssignment
from .base_admin import BaseModelAdmin
from django.utils.html import format_html
from django.db.models import Count


@admin.register(OrganisationChartPositionAssignment)
class OrganisationChartPositionAssignmentAdmin(BaseModelAdmin):
    """Admin interface for OrganisationChartPositionAssignment model"""
    
    list_display = [
        'positionAssignmentID',
        'position_title_with_level',
        'org_chart_link',
        'positionCode',
        'subordinates_count_display',
        'status_badge',
        'LastUpdate',
    ]

    list_filter = [
        'orgChartID',
        'positionLevel',
        'Suspended',
        'Lapsed',
        'DateAdded',
        'LastUpdate',
    ]

    search_fields = [
        'positionAssignmentID',
        'positionTitle',
        'positionCode',
        'positionDescription',
        'orgChartID__orgChartName',
        'LastUpdatedByID__email',
    ]

    readonly_fields = [
        'positionAssignmentID',
        'DateAdded',
        'LastUpdate',
        'subordinates_count_display',
        'hierarchy_info',
        'positionCode',
        'positionLevel',
    ]

    fieldsets = (
        ('Position Information', {
            'fields': (
                'positionTitle',
                'positionDescription',
                'positionCode',
                'positionLevel',
                'positionOrder',
            )
        }),
        ('Relationships', {
            'fields': (
                'orgChartID',
                'positionID',
                'positionParentID',
            )
        }),
        ('Hierarchy Information', {
            'fields': (
                'hierarchy_info',
                'subordinates_count_display',
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
                'positionAssignmentID',
                'DateAdded',
                'LastUpdate',
                'LastUpdatedByID',
            ),
            'classes': ('collapse',)
        }),
    )

    def position_title_with_level(self, obj):
        """Display position title with level"""
        return format_html(
            '{} <br><small style="color: #666;">{}</small>',
            obj.positionTitle,
            obj.positionLevel or 'No Level'
        )
    position_title_with_level.short_description = 'Position'
    position_title_with_level.admin_order_field = 'positionTitle'

    def org_chart_link(self, obj):
        """Create a clickable link to the org chart"""
        if obj.orgChartID:
            return format_html(
                '<a href="{}">{}</a>',
                f'/admin/core/organisationchart/{obj.orgChartID.orgChartID}/change/',
                obj.orgChartID.orgChartName
            )
        return "-"
    org_chart_link.short_description = 'Org Chart'
    org_chart_link.admin_order_field = 'orgChartID__orgChartName'

    def subordinates_count_display(self, obj):
        """Display count of subordinate positions"""
        count = obj.subordinates_count
        return format_html(
            '{} subordinate{} <br><small style="color: #666;">Direct reports</small>',
            count,
            's' if count != 1 else ''
        )
    subordinates_count_display.short_description = 'Subordinates'

    def hierarchy_info(self, obj):
        """Display hierarchy information"""
        superior = obj.get_superior()
        level = obj.get_hierarchy_level()
        
        info = [
            f"Hierarchy Level: {level}",
            f"Reports to: {superior.positionTitle if superior else 'Top Level'}"
        ]
        
        return format_html('<br>'.join(info))
    hierarchy_info.short_description = 'Hierarchy Information'

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
        obj.LastUpdatedByID = request.user
        super().save_model(request, obj, form, change)

    # Custom actions
    actions = ['suspend_positions', 'unsuspend_positions', 'lapse_positions', 'unlapse_positions']

    def suspend_positions(self, request, queryset):
        """Bulk suspend selected positions"""
        for obj in queryset:
            obj.suspend()
        self.message_user(request, f'{queryset.count()} positions were suspended.')
    suspend_positions.short_description = 'Suspend selected positions'

    def unsuspend_positions(self, request, queryset):
        """Bulk unsuspend selected positions"""
        for obj in queryset:
            obj.unsuspend()
        self.message_user(request, f'{queryset.count()} positions were unsuspended.')
    unsuspend_positions.short_description = 'Unsuspend selected positions'

    def lapse_positions(self, request, queryset):
        """Bulk lapse selected positions"""
        for obj in queryset:
            obj.lapse()
        self.message_user(request, f'{queryset.count()} positions were marked as lapsed.')
    lapse_positions.short_description = 'Mark selected positions as lapsed'

    def unlapse_positions(self, request, queryset):
        """Bulk unlapse selected positions"""
        for obj in queryset:
            obj.unlapse()
        self.message_user(request, f'{queryset.count()} positions were unmarked as lapsed.')
    unlapse_positions.short_description = 'Unmark selected positions as lapsed'

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/position_assignment_admin.js',)