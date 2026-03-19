from django.contrib import admin
from django.utils.html import format_html
from core.models.organisation_data import OrganisationData
from .base_admin import SoftDeleteAdmin

@admin.register(OrganisationData)
class OrganisationDataAdmin(SoftDeleteAdmin):
    list_display = (
        'get_org_info',
        'get_instance',
        'get_industry_sector',
        'get_contact_info',
        'get_status',
        'DateAdded',
    )

    search_fields = (
        'orgName',
        'orgEmail',
        'registrationNumber',
        'orgPIN',
        'orgCity',
        'orgCountry',
        'instanceID__instanceName',
        'industrySectorID__industryTitle',
    )

    list_filter = (
        'costCenterEnabled',
        'Lapsed',
        'Suspended',
        'orgCity',
        'orgCountry',
        'instanceID',
        'industrySectorID',
        'DateAdded',
    )

    readonly_fields = (
        'orgDataID',
        'DateAdded',
        'LastUpdate',
        'LastUpdatedByID',
    )

    fieldsets = (
        ('Organization Information', {
            'fields': (
                'orgName',
                'orgLogo',
                'instanceID',
                'industrySectorID',
                'numberOfEmployees',
            )
        }),
        ('Registration Details', {
            'fields': (
                'registrationNumber',
                'orgPIN',
                'costCenterEnabled',
            )
        }),
        ('Contact Information', {
            'fields': (
                'orgAddress',
                'orgPostalCode',
                'orgCity',
                'orgCountry',
                'orgPhoneNumber1',
                'orgPhoneNumber2',
                'orgEmail',
            )
        }),
        ('Status', {
            'fields': (
                'Lapsed',
                'Suspended',
            ),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': (
                'orgDataID',
                'DateAdded',
                'LastUpdate',
                'LastUpdatedByID',
            ),
            'classes': ('collapse',)
        }),
    )

    autocomplete_fields = ['instanceID', 'industrySectorID']

    def get_org_info(self, obj):
        """Display organization name with logo"""
        return format_html(
            '<div class="org-info"><img src="{}" class="org-logo" width="20" height="20"/> <strong>{}</strong></div>',
            obj.orgLogo,
            obj.orgName
        )
    get_org_info.short_description = 'Organization'
    get_org_info.admin_order_field = 'orgName'

    def get_instance(self, obj):
        """Display instance information"""
        return obj.instanceID.instanceName
    get_instance.short_description = 'Instance'
    get_instance.admin_order_field = 'instanceID__instanceName'

    def get_industry_sector(self, obj):
        """Display industry sector information"""
        return obj.industrySectorID.industryTitle
    get_industry_sector.short_description = 'Industry Sector'
    get_industry_sector.admin_order_field = 'industrySectorID__industryTitle'

    def get_contact_info(self, obj):
        """Display contact information"""
        return format_html(
            '<div class="contact-info">'
            '<small>{}</small><br>'
            '<small>📞 {}</small><br>'
            '<small>✉️ {}</small>'
            '</div>',
            f"{obj.orgCity}, {obj.orgCountry}",
            obj.orgPhoneNumber1,
            obj.orgEmail
        )
    get_contact_info.short_description = 'Contact Information'

    def get_status(self, obj):
        """Display status with indicators"""
        statuses = []
        if obj.Suspended == 'YES':
            statuses.append(format_html('<span style="color: red;">Suspended</span>'))
        if obj.Lapsed == 'YES':
            statuses.append(format_html('<span style="color: orange;">Lapsed</span>'))
        if obj.costCenterEnabled == 'ENABLED':
            statuses.append(format_html('<span style="color: green;">Cost Center</span>'))
        
        return format_html(' | '.join(statuses)) if statuses else '-'
    get_status.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        """Track who updated the organization"""
        obj.LastUpdatedByID = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimize queryset with related fields"""
        return super().get_queryset(request).select_related(
            'instanceID',
            'industrySectorID',
            'LastUpdatedByID'
        )

    class Media:
        css = {
            'all': ('admin/css/organisation_data_admin.css',)
        }
        js = ('admin/js/organisation_data_admin.js',)