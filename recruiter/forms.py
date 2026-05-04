from django.forms import ModelForm
from .models import Post, CustomUser, Skill, Company, RepresentativeProfile, ApplicantProfile, Application
from django.contrib.auth.forms import UserCreationForm, UserChangeForm



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'user_type', 'profile_picture']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

class JobForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'salary', 'skills_required']


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category', 'description']


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'location', 'website', 'description', 'industry', 'size', 'logo']


class RepresentitativeProfileForm(ModelForm):
    class Meta:
        model = RepresentativeProfile
        fields = ['position', 'department', 'phone']


class ApplicantProfileForm(ModelForm):
    class Meta:
        model = ApplicantProfile
        fields = ['cv', 'summary', 'experience_years', 'skills', 'location_preference', 'expected_salary']


class JobApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'expected_salary']
    