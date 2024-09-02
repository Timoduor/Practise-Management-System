from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
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
    last_updated_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING,related_name='%(class)s_last_updated_by')
    created_by = models.ForeignKey("core.User",null=True, blank=True ,on_delete=models.DO_NOTHING, related_name='%(class)s_created_by')


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

    def __str__(self):
        return self.name


class Entity(SoftDeleteModel):
    ENTITY_TYPES = [
        ("SEC","Single Entity Company"),
        ("HC","Holding Company")
        ]
    
    name =  models.CharField(max_length=30)
    entity_type = models.CharField(max_length=15, choices=ENTITY_TYPES, default="Single Entity Company")
    description = models.TextField()
    instance = models.ForeignKey("Instance", on_delete= models.SET_NULL,blank=True, null=True )
    parent_entity = models.ForeignKey("self", on_delete= models.SET_NULL,blank=True, null=True)

    def __str__(self):
        return self.name

class Unit(SoftDeleteModel):
    UNIT_TYPES = [
        ("BR","Branch"),
        ("DEP","Department"),
        ("SEC","Section"),
        ("TEA","Team")
    ]

    name = models.CharField(max_length=15)
    address = models.TextField(null=True, blank= True)
    unit_type = models.CharField(max_length=3, choices=UNIT_TYPES, default="DEP")
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL,blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        admin_type, created = AdminType.objects.get_or_create(
            name="SUP",
            defaults={"description": "Superuser with all permissions",
                    "created_by": user,
                    'last_updated_by': user
                    }
        )   

        # Create Admin entry
        Admin.objects.get_or_create(
            user=user,
            defaults={
                'admin_type': admin_type,
                'jurisdiction_content_type': None,
                'jurisdiction_object_id': None,
                'last_updated_by' : None,
                'created_by': None
            }
        )

        return

class User(AbstractUser):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    other_names = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No required fields for createsuperuser

    objects = CustomUserManager()

    def __str__(self):

        if self.first_name == None and self.last_name== None:
            name = self.email 
        else:
            name = f"{self.first_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"


    def delete(self, using=None, keep_parents=False):
        self.is_active = True
        self.save()

    def hard_delete(self):
        super().delete()

    def undelete(self):
        self.is_active = False
        self.save()

    def hard_delete(self):
        super().delete()

    def undelete(self):
        self.is_active = False
        self.save()


class Employee (SoftDeleteModel):
    """"

    """
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="employee_user")

    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null= True)



class AdminType(SoftDeleteModel):


    name = models.CharField(max_length= 15)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name

class Admin(SoftDeleteModel):

    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="admin_user")
    admin_type = models.ForeignKey(AdminType,on_delete=models.SET_NULL, null=True, blank=True)
    
    jurisdiction_content_type  = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    jurisdiction_object_id = models.PositiveIntegerField(blank=True, null=True)
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



