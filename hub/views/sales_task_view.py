from rest_framework.permissions import IsAuthenticated
from .common_viewset import CommonViewSet
from hub.serializers.sales_task_serializer import SalesTaskSerializer
from hub.models.sales_task import SalesTask


class SalesTaskViewSet(CommonViewSet):
    queryset = SalesTask.objects.all()
    serializer_class = SalesTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            match user.admin_user.admin_type.name:
                case "SUP":
                  return SalesTask.objects.all()
                case "INS":
                  return SalesTask.objects.filter(sale__entity__instance = user.employee_user.instance)
                case "ENT":
                    return SalesTask.objects.filter(sale__entity= user.employee_user.entity)  
                case "UNI":
                    return SalesTask.objects.filter(sale__unit= user.employee_user.unit)

        return SalesTask.objects.filter(sale__unit = user.employee_user.entity)

