from django.db import models
from .admin import Admin
from .admin_type import AdminType
from django.contrib.auth.models import AbstractUser, BaseUserManager



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
            defaults={"description": "Superuser with all permissions"
                      #"created_by": user,
                      #'last_updated_by': user
                    }
        )

        # Create an Admin entry for the superuser
        Admin.objects.get_or_create(
            user=user,
            defaults={
                'admin_type': admin_type,
                'jurisdiction_content_type': None,
                'jurisdiction_object_id': None,
                #'last_updated_by': None,
                #'created_by': None
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
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set on record creation
    last_updated_by = models.ForeignKey("core.User", null=True, blank=True, on_delete=models.DO_NOTHING, related_name='%(class)s_last_updated_by')  # User who last updated
    created_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='created_users'
    )


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
