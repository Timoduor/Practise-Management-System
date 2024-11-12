from django.db import models


class TaskType(models.Model):
    
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Task Type'
        verbose_name_plural = 'Task Types'

    def __str__(self):
        return self.name

