from django.contrib import admin
from .import models
from .forms import CustomUserChangeForm, CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.
@admin.register(models.CustomUser)
class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Use the same structure as default UserAdmin
    list_display = ('email', 'user_type', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ['profile_picture'],
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ['profile_picture'],
        }),
    )

admin.site.register(models.Post)
admin.site.register(models.Skill)
admin.site.register(models.ApplicantProfile)
admin.site.register(models.RepresentativeProfile)
admin.site.register(models.Proposal)
admin.site.register(models.Comment)
admin.site.register(models.Application)
admin.site.register(models.Company)