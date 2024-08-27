from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
# Create your models here.


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True)

    def hard_delete(self):
        return super().delete()

    def undelete(self):
        return super().update(is_deleted=False)

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # This manager includes deleted instances

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        super().delete()

    def undelete(self):
        self.is_deleted = False
        self.save()


class Instance(SoftDeleteModel):
    INDUSTRY_CHOICES = []

    name = models.CharField(max_length=30)
    code = models.CharField(max_length=10)
    industry = models.CharField(max_length=15)


class Entity(SoftDeleteModel):
    ENTITY_TYPES = [
        ("SEC","Single Entity Company"),
        ("HC","Holding Company")
        ]
    
    name =  models.CharField(max_length=30)
    entity_type = models.CharField(max_length=15, choices=ENTITY_TYPES, default="Single Entity Company")
    description = models.TextField()
    instance = models.ForeignKey("Instance", on_delete= models.SET_NULL,blank=True, null=True )
    parent_id = models.ForeignKey("self", on_delete= models.SET_NULL,blank=True, null=True)

class Unit(SoftDeleteModel):
    UNIT_TYPES = [
        ("BR","Branch"),
        ("DEP","Department"),
        ("SEC","Section"),
        ("TEA","Team")
    ]

    name = models.CharField(max_length=15)
    address = models.TextField(null=True, blank= True)
    unit_type = models.CharField(choices=UNIT_TYPES),
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL,blank=True, null=True)

    def __str__(self) -> str:
        return self.name

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    other_names = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username"]
    


class Employee (SoftDeleteModel):
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)

    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null= True)



class AdminType(SoftDeleteModel):
    ADMIN_TYPES = [
        ("SUP", "SuperUser" ),
        ("INS", "Instance Admin"),
        ("ENT", "Entity Admin"),
        ("UNI", "Unit Admin")
    ]

    name = models.CharField(max_length=30, choices=ADMIN_TYPES)
    description = models.TextField()

class Admin(SoftDeleteModel):

    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    admin_type = models.ForeignKey(AdminType,on_delete=models.SET_NULL, null=True, blank=True)
    
    jurisdiction_content_type  = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    jurisdiction_object_id = models.PositiveIntegerField()
    jurisdiction = GenericForeignKey("jurisdiction_content_type", "jurisdiction_object_id")


    def save(self, *args, **kwargs):
        if self.admin_type.name == "ENT":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Entity)
        elif self.admin_type.name == "UNI":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Unit)
        elif self.admin_type.name == "INS":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Instance)
        else:
            self.jurisdiction_content_type =None
            self.jurisdiction_object_id = None
            self.jurisdiction = None
            self.is_superuser = True
        
        super().save(*args, **kwargs)



