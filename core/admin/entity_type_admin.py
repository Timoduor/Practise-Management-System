from django.contrib import admin
from django.utils.html import format_html
from core.models.entity_type import EntityType
from .base_admin import SoftDeleteAdmin
from django.db import models

@admin.register(EntityType)
class EntityTypeAdmin(SoftDeleteAdmin):
    list_display = (
        'get_entity_type_title',
        'get_status',
        'get_entities_count',
        'DateAdded',
        'LastUpdate',
    )

    search_fields = (
        'entityTypeTitle',
        'entityTypeDescription',
    )

    list_filter = (
        'is_deleted',
        'Lapsed',
        'Suspended',
        'DateAdded',
        'LastUpdate',
    )

    readonly_fields = (
        'entityTypeID',
        'DateAdded',
        'LastUpdate',
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
    )

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'entityTypeTitle',
                'entityTypeDescription',
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
        ('Audit Information', {
            'fields': (
                'entityTypeID',
                'DateAdded',
                'LastUpdate',
                'created_at',
                'created_by',
                'updated_at',
                'last_updated_by',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_entity_type_title(self, obj):
        """Display entity type title with description tooltip"""
        return format_html(
            '<span title="{}">{}</span>',
            obj.entityTypeDescription,
            obj.entityTypeTitle
        )
    get_entity_type_title.short_description = 'Entity Type'
    get_entity_type_title.admin_order_field = 'entityTypeTitle'

    def get_status(self, obj):
        """Display status with colored indicators"""
        status = []
        if obj.is_deleted:
            status.append(format_html('<span style="color: red;">Deleted</span>'))
        if obj.Suspended:
            status.append(format_html('<span style="color: orange;">Suspended</span>'))
        if obj.Lapsed:
            status.append(format_html('<span style="color: yellow;">Lapsed</span>'))
        if not any([obj.is_deleted, obj.Suspended, obj.Lapsed]):
            return format_html('<span style="color: green;">Active</span>')
        return format_html(' | '.join(status))
    get_status.short_description = 'Status'

    def get_entities_count(self, obj):
        """Display count of entities using this type"""
        count = obj.entities.count()
        return format_html(
            '<span class="entity-count">{}</span>',
            count
        )
    get_entities_count.short_description = 'Entities'
    get_entities_count.admin_order_field = 'entities__count'

    def get_queryset(self, request):
        """Optimize queryset with annotations"""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            models.Count('entities', distinct=True)
        )

    def save_model(self, request, obj, form, change):
        """Track who created/updated the entity type"""
        if not change:
            obj.created_by = request.user
        obj.last_updated_by = request.user
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/entity_type_admin.css',)
        }
        js = ('admin/js/entity_type_admin.js',)