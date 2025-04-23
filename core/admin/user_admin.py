from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from core.models.user import User
from core.models.admin import Admin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'get_full_name',
        'email',
        'get_phone',
        'get_admin_type',
        'get_status',
        'date_joined',
    )

    search_fields = (
        'first_name',
        'last_name',
        'other_names',
        'email',
        'phone_number',
    )

    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'date_joined',
        'admin_user__admin_type',
    )

    ordering = ('-date_joined',)

    fieldsets = (
        ('Personal Information', {
            'fields': (
                'first_name',
                'last_name',
                'other_names',
                'email',
                'phone_number',
                'dob',
            )
        }),
        ('Address Information', {
            'fields': ('address',),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'password',
            )
        }),
        ('Important Dates', {
            'fields': (
                'last_login',
                'date_joined',
            ),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': (
                'groups',
                'user_permissions',
            ),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'first_name',
                'last_name',
                'password1',
                'password2',
            ),
        }),
    )

    readonly_fields = (
        'last_login',
        'date_joined',
    )

    def get_full_name(self, obj):
        """Display full name with email"""
        names = [obj.first_name, obj.last_name]
        if obj.other_names:
            names.insert(1, obj.other_names)
        full_name = ' '.join(filter(None, names))
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            full_name or '(No name)',
            obj.email
        )
    get_full_name.short_description = 'Name'
    get_full_name.admin_order_field = 'first_name'

    def get_phone(self, obj):
        """Display phone number if available"""
        if obj.phone_number:
            return format_html('📞 {}', obj.phone_number)
        return '-'
    get_phone.short_description = 'Phone'
    get_phone.admin_order_field = 'phone_number'

    def get_admin_type(self, obj):
        """Display admin type if user is an admin"""
        try:
            admin = obj.admin_user
            if admin and admin.admin_type:
                return format_html(
                    '<span class="admin-type-tag">{}</span>',
                    admin.admin_type.name
                )
        except Admin.DoesNotExist:
            pass
        return '-'
    get_admin_type.short_description = 'Admin Type'

    def get_status(self, obj):
        """Display user status with indicators"""
        statuses = []
        if not obj.is_active:
            statuses.append(format_html('<span style="color: red;">Inactive</span>'))
        if obj.is_superuser:
            statuses.append(format_html('<span style="color: purple;">Superuser</span>'))
        if obj.is_staff:
            statuses.append(format_html('<span style="color: blue;">Staff</span>'))
        if not statuses and obj.is_active:
            return format_html('<span style="color: green;">Active</span>')
        return format_html(' | '.join(statuses))
    get_status.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        """Handle password hashing for new users"""
        if not change:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)

    class Media:
        css = {
            'all': ('admin/css/user_admin.css',)
        }
        js = ('admin/js/user_admin.js',)