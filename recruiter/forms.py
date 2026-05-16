from django.forms import ModelForm
from .models import Post, CustomUser, Skill, Company, RepresentativeProfile, ApplicantProfile, Application, Proposal
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError



class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'user_type', 'profile_picture']


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class UserProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_picture']

class JobForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'salary', 'skills_required']

class ProjectForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'budget', 'skills_required']

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
        fields = [
            'cv',
            'summary',
            'experience_years',
            'skills',
            'linkedin_url',
            'github_url',
            'portfolio_url',
            'location_preference',
            'expected_salary',
        ]


class JobApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'expected_salary']


class ProposalForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        if self.project:
            self.instance.project = self.project

    class Meta:
        model = Proposal
        fields = ['amount', 'description', 'cover_letter', 'estimated_duration']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')

        if self.project and amount and self.project.budget and amount > self.project.budget:
            raise ValidationError(f"Proposal amount (${amount}) cannot exceed project budget (${self.project.budget})")

        return amount
