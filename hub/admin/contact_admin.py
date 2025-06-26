from django.contrib import admin
from django import forms
from hub.models.contact import Contact
from core.models.user import User


class ContactAdminForm(forms.ModelForm):
    existing_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Select Existing User",
        help_text="Choose an existing user to link to this contact"
    )

    class Meta:
        model = Contact
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Pre-fill contact fields from existing user if available
        if self.initial.get('existing_user') and not self.instance.pk:
            user = self.initial['existing_user']
            self.fields['contact_name'].initial = f"{user.first_name} {user.last_name}".strip()
            self.fields['contact_email'].initial = user.email

    def clean(self):
        cleaned_data = super().clean()
        selected_user = cleaned_data.get("existing_user")
        contact_email = cleaned_data.get("contact_email")

        if not selected_user and contact_email:
            if User.objects.filter(email=contact_email).exists():
                raise forms.ValidationError(
                    f"A user with this email exists. Please select them using 'Select Existing User'."
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_user = self.cleaned_data.get("existing_user")

        if selected_user:
            instance.user = selected_user
            # Optional: auto-fill values from user
            if not instance.contact_name:
                instance.contact_name = f"{selected_user.first_name} {selected_user.last_name}".strip()
            if not instance.contact_email:
                instance.contact_email = selected_user.email

        if commit:
            instance.save()
        return instance


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    form = ContactAdminForm  # keep this if you want custom logic like auto-filling fields
    autocomplete_fields = ['user']  # 🟢 key to using the preexisting user dropdown

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ('Link Existing User', {
            'fields': ('user',),  # 🟢 top of form: select user
            'description': 'Select an existing user to link to this contact.'
        }),
        ('Contact Information', {
            'fields': (
                'contact_name',
                'contact_email',
                'contact_phone',
                'contact_address',
                'contact_role',
                'customer',
            )
        }),
        ('Meta Info', {
            'fields': ('created_at', 'updated_at', 'is_deleted'),
            'classes': ('collapse',),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Dynamically insert the custom field
        form.base_fields['existing_user'] = ContactAdminForm.base_fields['existing_user']
        return form

    list_display = (
        'contact_name', 'contact_email', 'contact_phone', 'contact_role',
        'customer', 'user', 'created_at', 'updated_at'
    )
    search_fields = ('contact_name', 'contact_email', 'contact_role')
    list_filter = ('customer', 'contact_role', 'is_deleted')
    
