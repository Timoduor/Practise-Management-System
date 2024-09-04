from .views import UserViewSet, AdminViewSet, EmployeeViewSet, InstanceViewSet, UnitViewSet, EntityViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'admins', AdminViewSet,basename="admin")
router.register(r"employees", EmployeeViewSet, basename="employee")
router.register(r"instances", InstanceViewSet, basename="instance")
router.register(r"entities", EntityViewSet, basename="entity")
router.register(r"units", UnitViewSet, basename="unit")

urlpatterns = router.urls