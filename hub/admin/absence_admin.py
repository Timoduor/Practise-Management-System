from django.contrib import admin
from hub.models.absence import Absence

@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Absence Info", {"fields": ["absence_date", "start_time", "end_time", "absence_description", "leave_type"]}),
        ("Project", {"fields": ["project"]}),
        ("User", {"fields": ["user"]}),
    ]
    list_display = ('user', 'absence_date', 'start_time', 'end_time', 'leave_type', 'project', 'created_at', 'updated_at')
    search_fields = ('user__email', 'project__project_name')
    list_filter = ('leave_type', 'project', 'absence_date', 'is_deleted')
