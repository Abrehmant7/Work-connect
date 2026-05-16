from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from recruiter.forms import (
    ApplicantProfileForm,
    CompanyForm,
    RepresentitativeProfileForm,
    UserProfileForm,
)
from recruiter.models import RepresentativeProfile
from .common import (
    applicant_required,
    representative_profile_required,
    representative_required,
)


@login_required(login_url='login')
@representative_required
def complete_representative_profile(request):
    profile = getattr(request.user, 'representative_profile', None)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        form = RepresentitativeProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and form.is_valid():
            user_form.save()
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, "Profile saved successfully!")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserProfileForm(instance=request.user)
        form = RepresentitativeProfileForm(instance=profile)

    return render(request, "profiles/representative_profile.html", {
        'form': form,
        'user_form': user_form,
        'profile': profile,
    })


@login_required(login_url='login')
@applicant_required
def complete_applicant_profile(request):
    profile = getattr(request.user, 'applicant_profile', None)

    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        form = ApplicantProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and form.is_valid():
            user_form.save()
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            form.save_m2m()
            messages.success(request, "Profile saved successfully!")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserProfileForm(instance=request.user)
        form = ApplicantProfileForm(instance=profile)

    return render(request, "profiles/applicant_profile.html", {
        'form': form,
        'user_form': user_form,
        'profile': profile,
    })


@login_required(login_url='login')
@representative_required
@representative_profile_required
def create_company(request):
    if request.user.representative_profile.company is not None:
        messages.error(request, "You already have a company in place!")
        return redirect('/')

    if request.method == 'POST':
        form = CompanyForm(request.POST, request.FILES)

        if form.is_valid():
            company = form.save()
            user_profile = get_object_or_404(RepresentativeProfile, user__pk=request.user.pk)
            user_profile.company = company
            user_profile.save()
            messages.success(request, "Company created successfully!")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        form = CompanyForm()

    return render(request, 'profiles/company_form.html', {'form': form})
