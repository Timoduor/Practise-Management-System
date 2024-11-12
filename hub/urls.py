from django.urls import path, include
from rest_framework.routers import DefaultRouter
from hub.views.absence_view import AbsenceViewSet
from hub.views.customer_view import CustomerViewSet
from hub.views.sales_view import SalesViewSet
from hub.views.contact_view import ContactViewSet
from hub.views.project_view import ProjectViewSet
from hub.views.project_phase_view import ProjectPhaseViewSet
from hub.views.task_view import TaskViewSet
from hub.views.invoice_view import InvoiceViewSet
from hub.views.work_entries_view import WorkEntriesViewSet
from hub.views.leave_type_view import LeaveTypeViewSet
from hub.views.expense_view import ExpenseViewSet
from hub.views.sales_task_view import SalesTaskViewSet
from hub.views.sales_task_type_view import SalesTaskTypeViewSet
from hub.views.sales_task_status_view import SalesTaskStatusViewSet
from hub.views.task_type_view import TaskTypeViewSet
from hub.views.task_status_view import TaskStatusViewSet
from hub.views.sales_type_view import SalesTypeViewSet
from hub.views.timesheet_view import TimesheetView


router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'sales', SalesViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'phases', ProjectPhaseViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'work-entries', WorkEntriesViewSet)
router.register(r'leavetypes', LeaveTypeViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'sales-tasks', SalesTaskViewSet)
router.register(r'sales-task-types', SalesTaskTypeViewSet)
router.register(r'sales-task-statuses', SalesTaskStatusViewSet)
router.register(r'task-types', TaskTypeViewSet)
router.register(r'task-statuses', TaskStatusViewSet)
router.register(r'sales-types', SalesTypeViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('dashboard/timesheets/', TimesheetView.as_view(), name="timesheet-dashboard"),
]
