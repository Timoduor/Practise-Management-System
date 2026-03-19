from django.contrib import admin
from django.utils.html import format_html
from core.models.admin import Admin
from .base_admin import SoftDeleteAdmin
from core.models.admin_type import AdminType
from django import forms

class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = [
            'user', 'admin_type', 'entity', 'unit', 'instance',
            'is_deleted', 'created_by', 'last_updated_by'
        ]

    def clean(self):
        cleaned_data = super().clean()
        print("FORM DEBUG:", cleaned_data)
        admin_type = cleaned_data.get('admin_type')
        entity = cleaned_data.get('entity')
        unit = cleaned_data.get('unit')
        instance = cleaned_data.get('instance')

        if admin_type:
            if admin_type.name == "ENT":
                if not entity:
                    raise forms.ValidationError("Entity must be set for ENT admin type.")
            elif admin_type.name == "UNI":
                if not unit:
                    raise forms.ValidationError("Unit must be set for UNI admin type.")
            elif admin_type.name == "INS":
                if not instance:
                    raise forms.ValidationError("Instance must be set for INS admin type.")
        return cleaned_data

@admin.register(Admin)
class AdminAdmin(SoftDeleteAdmin):
    form = AdminForm
    list_display = (
        'user',
        'admin_type',
        'get_jurisdiction',
        'is_active',
        'created_at',
    )

    search_fields = (
        'user__email',
        'user__firstName',
        'user__surname',
        'admin_type__name',
    )

    list_filter = (
        'is_deleted',
        'admin_type',
        'jurisdiction_content_type',
        'created_at',
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'created_by',
        'last_updated_by',
        'jurisdiction_content_type',
        'jurisdiction_object_id',
    )

    """
     def save_model(self, request, obj, form, change):
        obj = form.save(commit=False)
        admin_type = form.cleaned_data.get('admin_type')
        obj.entity = form.cleaned_data.get('entity')
        obj.unit = form.cleaned_data.get('unit')
        obj.instance = form.cleaned_data.get('instance')
 
        if admin_type:
            if admin_type.name == "ENT":
                obj.unit = None
                obj.instance = None
            elif admin_type.name == "UNI":
                obj.entity = None
                obj.instance = None
            elif admin_type.name == "INS":
                obj.instance = form.cleaned_data.get('instance')
                obj.entity = None
                obj.unit = None
            else:
                obj.entity = None
                obj.unit = None
                obj.instance = None
        else:
            obj.entity = None
            obj.unit = None
            obj.instance = None

        print("ADMIN DEBUG:", obj.admin_type, obj.entity, obj.unit, obj.instance)
        obj.save()
        form.save_m2m()
        """
    
    def save_model(self, request, obj, form, change):
        print(">>> ENTERED save-model")
        """
        at = form.cleaned_data.get('admin_type')
        ent = form.cleaned_data.get('entity')
        uni = form.cleaned_data.get('unit')
        ins = form.cleaned_data.get('instance')

        obj.entity = obj.unit = obj.instance = None

        if at:
            if at.name == "ENT":
               obj.entity = ent
        elif at.name == "UNI":
               obj.unit = uni 
        elif at.name == "INS":
               obj.instance = ins

        print("ADMIN DEBUG (before save):", at, obj.entity, obj.unit, obj.instance)
        """
    # This ensures Django's admin properly saves the model
        super().save_model(request, obj, form, change)
    # Save any many-to-many relations
        form.save_m2m()
        
        
    def get_jurisdiction(self, obj):
        """Display jurisdiction information"""
        if obj.jurisdiction_content_type and obj.jurisdiction_object_id:
            content_type = obj.jurisdiction_content_type.model.title()
            try:
                jurisdiction_obj = obj.jurisdiction
                return format_html(
                    '<span title="{}: {}">{} ({})</span>',
                    content_type,
                    jurisdiction_obj,
                    content_type,
                    obj.jurisdiction_object_id
                )
            except Exception:
                return f"{content_type} ({obj.jurisdiction_object_id})"
        return "Global Admin"
    get_jurisdiction.short_description = 'Jurisdiction'
    get_jurisdiction.admin_order_field = 'jurisdiction_content_type'

    def is_active(self, obj):
        """Display active status with color indicator"""
        if not obj.is_deleted:
            return format_html(
                '<span style="color: green;">●</span> Active'
            )
        return format_html(
            '<span style="color: red;">●</span> Inactive'
        )
    is_active.short_description = 'Status'
    is_active.admin_order_field = 'is_deleted'

    fieldsets = (
        ('Admin Information', {
            'fields': (
                'user',
                'admin_type',
            )
        }),
        ('Jurisdiction', {
            'fields': (
                'entity',
                'unit',
                'instance',
            ),
            'description': 'Specify the scope of administrative control'
        }),
        ('Status Information', {
            'fields': (
                'is_deleted',
                'created_at',
                'created_by',
                'updated_at',
                'last_updated_by',
            ),
            'classes': ('collapse',)
        }),
    )

    class Media:
        css = {
            'all': ('admin/css/admin_admin.css',)
        }