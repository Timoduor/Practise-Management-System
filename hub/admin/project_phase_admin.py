from django.contrib import admin
from hub.models.project_phase import ProjectPhase

@admin.register(ProjectPhase)
class ProjectPhaseAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Phase Info", {"fields": ["phase_name", "phase_description", "start_date", "end_date"]}),
        ("Associated Project", {"fields": ["project"]}),
    ]
    list_display = ('phase_name', 'project', 'start_date', 'end_date', 'created_at', 'updated_at')
    search_fields = ('phase_name', 'project__project_name')
    list_filter = ('start_date', 'end_date', 'is_deleted')
