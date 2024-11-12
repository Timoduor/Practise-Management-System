from django.db import models

class SalesTaskType(models.Model):

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sales Task Type'
        verbose_name_plural = 'Sales Task Types'

    def __str__(self):
        return self.name

