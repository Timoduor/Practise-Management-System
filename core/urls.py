from core.views.admin_views import AdminViewSet
from core.views.employee_views import EmployeeViewSet
from core.views.instance_views import InstanceViewSet
from core.views.entity_views import EntityViewSet
from core.views.user_views import UserViewSet
from core.views.unit_views import UnitViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'admins', AdminViewSet,basename="admin")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"instances", InstanceViewSet, basename="instance")
router.register(r"entities", EntityViewSet, basename="entity")
router.register(r"units", UnitViewSet, basename="unit")

urlpatterns = router.urls