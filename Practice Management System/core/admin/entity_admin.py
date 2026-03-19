from django.contrib import admin
from django.utils.html import format_html
from core.models.entity import Entity
from .base_admin import SoftDeleteAdmin, JurisdictionInline

@admin.register(Entity)
class EntityAdmin(SoftDeleteAdmin):
    list_display = (
        'entityName',
        'get_entity_type',
        'get_instance',
        'get_parent_entity',
        'get_industry',
        'is_active',
        'DateAdded',
    )

    search_fields = (
        'entityName',
        'entityDescription',
        'entityTypeID__name',
        'instanceID__name',
        'entityParentID__entityName',
        'industrySectorID__industryTitle',
        'registrationNumber',
        'entityPIN',
    )

    list_filter = (
        'is_deleted',
        'entityTypeID',
        'instanceID',
        'industrySectorID',
        'entityCity',
        'entityCountry',
        'Lapsed',
        'Suspended',
    )

    autocomplete_fields = [
        'entityTypeID',
        'instanceID',
        'orgDataID',
        'entityParentID',
        'industrySectorID',
    ]

    readonly_fields = (
        'DateAdded',
        'LastUpdate',
        'LastUpdateByID',
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'entityName',
                'entityDescription',
                'entityTypeID',
                'instanceID',
            )
        }),
        ('Organization Structure', {
            'fields': (
                'orgDataID',
                'entityParentID',
                'industrySectorID',
            ),
        }),
        ('Registration Details', {
            'fields': (
                'registrationNumber',
                'entityPIN',
            ),
        }),
        ('Contact Information', {
            'fields': (
                'entityCity',
                'entityCountry',
                'entityPhoneNumber',
                'entityEmail',
            ),
        }),
        ('Status', {
            'fields': (
                'Lapsed',
                'Suspended',
                'is_deleted',
            ),
            'classes': ('collapse',)
        }),
        ('Audit Information', {
            'fields': (
                'DateAdded',
                'LastUpdate',
                'LastUpdateByID',
                'created_at',
                'created_by',
                'updated_at',
                'last_updated_by',
            ),
            'classes': ('collapse',)
        }),
    )

    inlines = [JurisdictionInline]

    def get_entity_type(self, obj):
        if obj.entityTypeID:
            return format_html(
                '<span class="entity-type-tag">{}</span>',
                obj.entityTypeID
            )
        return "-"
    get_entity_type.short_description = 'Type'
    get_entity_type.admin_order_field = 'entityTypeID__name'

    def get_instance(self, obj):
        if obj.instanceID:
            return format_html(
                '<span class="instance-tag">{}</span>',
                obj.instanceID
            )
        return "-"
    get_instance.short_description = 'Instance'
    get_instance.admin_order_field = 'instanceID__name'

    def get_parent_entity(self, obj):
        if obj.entityParentID:
            return format_html(
                '<span class="parent-entity-tag">{}</span>',
                obj.entityParentID.entityName
            )
        return "-"
    get_parent_entity.short_description = 'Parent Entity'
    get_parent_entity.admin_order_field = 'entityParentID__entityName'

    def get_industry(self, obj):
        if obj.industrySectorID:
            return format_html(
                '<span class="industry-tag">{}</span>',
                obj.industrySectorID
            )
        return "-"
    get_industry.short_description = 'Industry'
    get_industry.admin_order_field = 'industrySectorID__industryTitle'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.LastUpdateByID = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/entity_admin.css',)
        }
        js = ('admin/js/entity_admin.js',)