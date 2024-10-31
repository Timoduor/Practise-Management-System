# Import necessary Django modules for models and user management
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Define a queryset for models with soft delete functionality
class SoftDeleteQuerySet(models.QuerySet):

    def delete(self):
        # Perform a soft delete by updating `is_deleted` to True
        return super().update(is_deleted=True)

    def hard_delete(self):
        # Permanently delete the record from the database
        return super().delete()

    def undelete(self):
        # Restore a soft-deleted record by setting `is_deleted` to False
        return super().update(is_deleted=False)

# Define a manager for models with soft delete functionality
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Override the default queryset to exclude soft-deleted records
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

# Define a base model with soft delete functionality and timestamp tracking
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)  # Field to mark soft deletion status
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on record creation
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated on record update
    last_updated_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(class)s_last_updated_by')  # User who last updated
    created_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(class)s_created_by')  # User who created

    # Managers for handling soft-deleted records
    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Manager that includes soft-deleted records

    class Meta:
        abstract = True  # Abstract base class, won't create a table

    def delete(self, using=None, keep_parents=False):
        # Override delete method to perform a soft delete
        self.is_deleted = True
        self.save()

    def hard_delete(self):
        # Permanently delete the instance
        super().delete()

    def undelete(self):
        # Restore a soft-deleted instance
        self.is_deleted = False
        self.save()

# Define an Instance model that represents a company instance with industry info
class Instance(SoftDeleteModel):
    INDUSTRY_CHOICES = []  # Placeholder for industry choices

    name = models.CharField(max_length=30)  # Instance name
    code = models.CharField(max_length=20)  # Short code for instance
    industry = models.CharField(max_length=30)  # Industry type

    def __str__(self):
        return self.name  # String representation of the instance

# Define an Entity model to represent entities within instances, like companies
class Entity(SoftDeleteModel):
    ENTITY_TYPES = [
        ("SEC", "Single Entity Company"),
        ("HC", "Holding Company")
    ]

    name = models.CharField(max_length=30)  # Entity name
    entity_type = models.CharField(max_length=15, choices=ENTITY_TYPES, default="Single Entity Company")
    description = models.TextField()  # Description of the entity
    instance = models.ForeignKey("Instance", on_delete=models.SET_NULL, blank=True, null=True, related_name="entities")  # Related instance
    parent_entity = models.ForeignKey("self", on_delete=models.SET_NULL, blank=True, null=True)  # Optional parent entity for hierarchy

    def __str__(self):
        return f"{self.instance} - {self.name}"  # String representation

# Define a Unit model representing smaller divisions within an entity (e.g., branches)
class Unit(SoftDeleteModel):
    UNIT_TYPES = [
        ("BR", "Branch"),
        ("DEP", "Department"),
        ("SEC", "Section"),
        ("TEA", "Team")
    ]

    name = models.CharField(max_length=15)  # Unit name
    address = models.TextField(null=True, blank=True)  # Optional unit address
    unit_type = models.CharField(max_length=3, choices=UNIT_TYPES, default="DEP")  # Unit type
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, blank=True, null=True, related_name="units")  # Related entity

    def __str__(self):
        return f"{self.entity} - {self.name}"  # String representation

# Define a custom user manager to handle user creation and superuser creation
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
        # Set staff and superuser status for a superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # Validate that superuser has necessary permissions
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Create superuser and assign "SUP" admin type
        user = self.create_user(email, password, **extra_fields)
        admin_type, created = AdminType.objects.get_or_create(
            name="SUP",
            defaults={"description": "Superuser with all permissions",
                      "created_by": user,
                      'last_updated_by': user}
        )

        # Create an Admin entry for the superuser
        Admin.objects.get_or_create(
            user=user,
            defaults={
                'admin_type': admin_type,
                'jurisdiction_content_type': None,
                'jurisdiction_object_id': None,
                'last_updated_by': None,
                'created_by': None
            }
        )
        return user

# Define custom User model extending AbstractUser to add additional fields
class User(AbstractUser):
    first_name = models.CharField(max_length=30)  # User's first name
    last_name = models.CharField(max_length=30)  # User's last name
    other_names = models.CharField(max_length=30)  # Additional names
    email = models.EmailField(unique=True)  # Unique email used for login
    phone_number = models.CharField(max_length=20, blank=True, null=True)  # Optional phone number
    address = models.TextField(blank=True, null=True)  # Optional address
    dob = models.DateField(blank=True, null=True)  # Optional date of birth

    # Set email as the unique identifier for authentication
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No extra fields required for createsuperuser

    objects = CustomUserManager()  # Use the custom manager

    def __str__(self):
        # Return either the user's email or full name
        name = self.email if self.first_name is None and self.last_name is None else f"{self.first_name} {self.last_name}"
        return name

    def delete(self, using=None, keep_parents=False):
        # Override delete method to perform a soft delete (deactivate account)
        self.is_active = False
        self.save()

    def hard_delete(self):
        # Permanently delete the user
        super().delete()

    def undelete(self):
        # Reactivate a soft-deleted user
        self.is_active = True
        self.save()

# Define Employee model to link users to instances, entities, and units
class Employee(SoftDeleteModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="employee_user")  # Linked user account
    instance = models.ForeignKey("Instance", on_delete=models.CASCADE)  # Related instance
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE, blank=True, null=True)  # Related entity
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, blank=True, null=True)  # Optional unit

# Define AdminType model to categorize admin types
class AdminType(SoftDeleteModel):
    name = models.CharField(max_length=15)  # Type name (e.g., "SUP")
    description = models.TextField()  # Description of the admin type

    def __str__(self) -> str:
        return self.name  # String representation of the admin type

# Define Admin model to link users with admin roles and permissions
class Admin(SoftDeleteModel):
    user = models.OneToOneField("core.User", on_delete=models.CASCADE, related_name="admin_user")  # Linked user
    admin_type = models.ForeignKey(AdminType, on_delete=models.SET_NULL, null=True, blank=True)  # Admin type

    # Define jurisdiction for admin based on ContentType and object ID
    jurisdiction_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, blank=True, null=True)
    jurisdiction_object_id = models.PositiveIntegerField(blank=True, null=True)
    jurisdiction = GenericForeignKey("jurisdiction_content_type", "jurisdiction_object_id")

    def save(self, *args, **kwargs):
        # Automatically set the jurisdiction type based on admin_type
        if self.admin_type.name == "ENT":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Entity)
        elif self.admin_type.name == "UNI":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Unit)
        elif self.admin_type.name == "INS":
            self.jurisdiction_content_type = ContentType.objects.get_for_model(Instance)
        else:
            self.jurisdiction_content_type = None
            self.jurisdiction_object_id = None
            self.jurisdiction = None
            self.is_superuser = True

        # Save the instance with updated values
        super().save(*args, **kwargs)
