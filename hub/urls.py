from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, ContactViewSet, SalesViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'sales', SalesViewSet)

urlpatterns = router.urls
