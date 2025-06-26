from core.views.admin_views import AdminViewSet
from core.views.employee_views import EmployeeViewSet
from core.views.instance_views import InstanceViewSet
from core.views.entity_views import EntityViewSet
from core.views.user_views import UserViewSet, UserDropdownViewSet
from core.views.unit_views import UnitViewSet
from rest_framework.routers import DefaultRouter
from core.views.entity_type_views import EntityTypeViewSet
from core.views.unit_type_views import UnitTypeViewSet
from core.views.admin_type_views import AdminTypeViewSet
from core.views.organisation_chart_views import OrganisationChartViewSet
from core.views.organisation_chart_position_assignments_views import OrganisationChartPositionAssignmentViewSet
from core.views.organisation_data_views import OrganisationDataViewSet
from core.views.organisation_permission_views import OrganisationRoleViewSet
from core.views.permission_profile_views import PermissionProfileViewSet 
from core.views.permissions_views import PermissionViewSet


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
router.register('organisation-positions', OrganisationChartPositionAssignmentViewSet,basename='organisation_position')
router.register('organisation-charts', OrganisationChartViewSet,basename='organisation_chart')
router.register(r"organisation-data", OrganisationDataViewSet, basename="organisation_data")
router.register(r'organisation-roles', OrganisationRoleViewSet, basename='organisationrole')
router.register(r'permission-profiles', PermissionProfileViewSet, basename='permissionprofile')
router.register(r'user-dropdown', UserDropdownViewSet, basename='user_dropdown')
router.register(r'permissions', PermissionViewSet, basename='permission')
urlpatterns = router.urls

