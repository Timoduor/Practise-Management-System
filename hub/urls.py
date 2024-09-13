from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, ContactViewSet, ProjectViewSet, TaskViewSet, SalesViewSet, InvoiceViewSet, ProjectPhaseViewSet, WorkEntriesViewSet,LeaveTypeViewSet, AbsenceViewSet, ExpenseViewSet

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


urlpatterns = router.urls
