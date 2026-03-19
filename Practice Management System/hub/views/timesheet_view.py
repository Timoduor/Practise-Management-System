from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from hub.models.absence import Absence
from hub.models.work_entries import WorkEntries
from hub.models.expense import Expense
from django.utils.timezone import now
from datetime import datetime, timedelta
from rest_framework.views import APIView
from collections import defaultdict

class TimesheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        current_date = now().date()
        editable_date = current_date - timedelta(days=7)

        week_str = request.query_params.get('week', None)

        # If no week is provided, use current week starting Monday
        if week_str:
            dt = datetime.strptime(week_str, '%Y-%m-%d').date()
            week_start = dt - timedelta(days=dt.weekday())
        else:
            week_start = current_date - timedelta(days=current_date.weekday())

        week_end = week_start + timedelta(days=6)

        # Group work_entries, absences, and expenses by day
        data = defaultdict(lambda: {
            'work_entries': [],
            'absences': [],
            'expenses': []
        })

        # Query WorkEntries for the selected week.
        # Removed start_time and end_time since those fields no longer exist.
        # Now including the supporting_document field.
        work_entries = WorkEntries.objects.filter(
            user=user, date__range=[week_start, week_end]
        ).values(
            'work_entries_id',
            'date',
            'duration',
            'supporting_document',  # NEW: include the file field
            'task_type__name',
            'customer__customer_name',
            'task_id',
            'task__task_name',
            'project__project_name',
            'phase__phase_name',
            'sale',
            'sale__sales_name',
            'sales_task__task_name',
            'description'
        )

        # Query Absences for the selected week.
        absences = Absence.objects.filter(
            user=user, absence_date__range=[week_start, week_end]
        ).values(
            'absence_id',
            'absence_date',
            'start_time',
            'end_time',
            'duration',
            'leave_type',
            'leave_type__name',
            'project_id',
            'project__project_name',
            'sale',
            'sale__sales_name',
            'absence_description',
            'supporting_document'
        )

        # Query Expenses for the selected week.
        expenses = Expense.objects.filter(
            user=user, date__range=[week_start, week_end]
        ).values(
            'expense_id',
            'date',
            'value',
            'description',
            'supporting_document',
            'task_id',
            'task__task_name',
            'customer__customer_name',
            'project__project_name',
            'phase__phase_name',
            'sale',
            'sale__sales_name',
            'sales_task_id',
            'sales_task__task_name'
        )

        # Helper: Convert timedelta to "HH:MM"
        def convert_timedelta_to_hours_minutes(duration):
            if duration != 0:
                total_seconds = duration.total_seconds()
            else:
                total_seconds = 0
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60) or "00"
            return f"{hours}:{minutes}"

        # Process work_entries and group them by day.
        for entry in work_entries:
            day_name = entry['date'].strftime('%A')
            entry['duration'] = convert_timedelta_to_hours_minutes(entry['duration'])
            entry['editable'] = entry['date'] >= editable_date
            data[day_name]['work_entries'].append(entry)

        # Process absences
        for absence in absences:
            day_name = absence['absence_date'].strftime('%A')
            absence['duration'] = convert_timedelta_to_hours_minutes(absence['duration'])
            absence['editable'] = absence['absence_date'] >= editable_date
            data[day_name]['absences'].append(absence)

        # Process expenses
        for expense in expenses:
            day_name = expense['date'].strftime('%A')
            expense['editable'] = expense['date'] >= editable_date
            data[day_name]['expenses'].append(expense)

        # Calculate totals
        total_work_hours = work_entries.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        total_absence_hours = absences.aggregate(total_duration=Sum('duration'))['total_duration'] or 0
        total_expenses = expenses.aggregate(total_expenses=Sum('value'))['total_expenses'] or 0

        formatted_work_duration = convert_timedelta_to_hours_minutes(total_work_hours)
        formatted_absence_duration = convert_timedelta_to_hours_minutes(total_absence_hours)

        # Ensure each day of the week exists
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for day in days_of_week:
            if day not in data:
                data[day] = {'work_entries': [], 'absences': [], 'expenses': []}

        response_data = {
            'week_start': week_start,
            'week_end': week_end,
            'total_work_duration': formatted_work_duration,
            'total_absence_duration': formatted_absence_duration,
            'total_expenses': total_expenses,
            'days': data
        }

        return Response(response_data)
