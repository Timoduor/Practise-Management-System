from django.db import models
from core.models.base import SoftDeleteModel
from core.models.employee import Employee
from core.models.entity import Entity
from core.models.instance import Instance
from core.models.unit import Unit
from .customer import Customer
from .sales import Sales


class Project(SoftDeleteModel):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=100)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="projects")
    project_description = models.TextField(blank=True, null=True)
    project_value = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    project_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name="project_manager")
    members = models.ManyToManyField(Employee, blank=True,  related_name="project_members")
    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, null=True, blank=True, related_name="related_project")
    
    instance = models.ForeignKey(Instance, on_delete=models.SET_NULL, blank=True, null=True)
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['start_date']
    
    def __str__(self):
        return self.project_name

