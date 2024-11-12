from django.contrib import admin
from hub.models.leave_type import LeaveType

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Leave Type Info", {"fields": ["name", "description", "is_paid"]}),
    ]
    list_display = ('name', 'is_paid', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('is_paid', 'created_at', 'updated_at')
