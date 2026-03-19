from django.db import models

class SalesStatus(models.Model):
   
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Sales Status'
        verbose_name_plural = 'Sales Status'

    def __str__(self):
        return self.name