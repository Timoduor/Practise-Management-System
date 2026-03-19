from core.views.admin_views import AdminViewSet
from core.views.employee_views import EmployeeViewSet
from core.views.instance_views import InstanceViewSet
from core.views.entity_views import EntityViewSet
from core.views.user_views import UserViewSet
from core.views.unit_views import UnitViewSet
from rest_framework.routers import DefaultRouter
from core.views.entity_type_views import EntityTypeViewSet
from core.views.unit_type_views import UnitTypeViewSet
from core.views.admin_type_views import AdminTypeViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'admins', AdminViewSet,basename="admin")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"instances", InstanceViewSet, basename="instance")
router.register(r"entities", EntityViewSet, basename="entity")
router.register(r"units", UnitViewSet, basename="unit")
router.register(r"entity-types", EntityTypeViewSet, basename="entity_type")
router.register(r"unit-types", UnitTypeViewSet, basename="unit_type")
router.register(r"admin-types", AdminTypeViewSet, basename="admin_type")


urlpatterns = router.urls

