from django.db import models

class SalesType(models.Model):
   
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sales Type'
        verbose_name_plural = 'Sales Types'

    def __str__(self):
        return self.name