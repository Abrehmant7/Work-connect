from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from recruiter.forms import JobApplicationForm, JobForm
from recruiter.models import Application, Post
from .common import (
    ACTIVE_STATUSES,
    applicant_profile_required,
    applicant_required,
    has_applicant_profile,
    is_applicant,
    is_representative,
    representative_profile_required,
    representative_required,
)


@login_required(login_url='login')
@representative_required
@representative_profile_required
def addJob(request):
    if not request.user.representative_profile.company:
        messages.info(request, "You have to register a company first!")
        return redirect('company_creation')

    saved_post_data = request.session.get('saved_post_form_data', {})

    if request.method == 'POST':
        form = JobForm(request.POST)

        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.post_type = 'job'
            job_post.created_by = request.user
            job_post.status = 'published'
            job_post.company = request.user.representative_profile.company
            job_post.published_at = timezone.now()
            job_post.save()
            form.save_m2m()

            request.session.pop('saved_post_form_data', None)
            request.session.pop('skill_return_url', None)

            messages.success(request, "Job created successfully!")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm(saved_post_data) if saved_post_data else JobForm()

    return render(request, "jobs/job_form.html", {'form': form})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def edit_job(request, job_id):
    job = get_object_or_404(Post, pk=job_id, post_type='job', created_by=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            job = form.save(commit=False)
            job.post_type = 'job'
            job.created_by = request.user
            job.company = request.user.representative_profile.company
            job.save()
            form.save_m2m()
            messages.success(request, "Job updated successfully!")
            return redirect("applications_for_job", job_id=job.pk)

        messages.error(request, "Please correct the errors below.")
    else:
        form = JobForm(instance=job)

    return render(request, "jobs/job_form.html", {'form': form, 'job': job, 'is_edit': True})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def delete_job(request, job_id):
    job = get_object_or_404(Post, pk=job_id, post_type='job', created_by=request.user)

    if request.method == 'POST':
        job.status = 'cancelled'
        job.is_active = False
        job.closed_at = timezone.now()
        job.save()
        messages.success(request, "Job deleted successfully.")
        return redirect("all_jobs_created")

    return render(request, "jobs/job_confirm_delete.html", {'job': job})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def view_all_jobs_created(request):
    jobs = Post.objects.filter(
        post_type='job',
        created_by=request.user,
        status__in=['filled', 'published', 'cancelled', 'closed'],
    ).order_by('-created_at')

    return render(request, 'jobs/all_jobs_created.html', {'jobs': jobs})


@login_required(login_url='login')
def view_applications_for_job(request, job_id):
    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("all_jobs_created")

    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.error(request, "You have to create profile first!")
        return redirect("representative_profile")

    job = get_object_or_404(Post, post_type='job', pk=job_id, created_by=request.user)
    accepted_application = job.applications.filter(status='accepted').first()
    applications = [] if accepted_application else job.applications.all()

    return render(request, "jobs/applications_for_job.html", {
        'applications': applications,
        'accepted_application': accepted_application,
        'job': job,
    })


@login_required(login_url='login')
@representative_required
@representative_profile_required
def view_application_detail(request, application_id):
    application = get_object_or_404(Application, pk=application_id, job__created_by=request.user)
    return render(request, 'jobs/application_detail.html', {'application': application})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def apply_to_job(request, job_pk):
    profile = getattr(request.user, "applicant_profile", None)
    job = get_object_or_404(Post, post_type='job', pk=job_pk, status='published', is_active=True)

    if Application.objects.filter(applicant=profile, job=job).exists():
        messages.error(request, "You already have an application for this job!")
        return redirect('view_job', slug=job.slug)

    if request.method == 'POST':
        form = JobApplicationForm(request.POST)

        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = profile
            application.job = job
            application.status = 'applied'
            application.save()
            messages.success(request, "Applied for the job successfully.")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        form = JobApplicationForm()

    return render(request, "jobs/application_form.html", {'form': form, 'job': job})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def edit_application(request, application_id):
    application = get_object_or_404(
        Application,
        pk=application_id,
        applicant=request.user.applicant_profile,
        status__in=ACTIVE_STATUSES,
    )

    if request.method == 'POST':
        form = JobApplicationForm(request.POST, instance=application)

        if form.is_valid():
            form.save()
            messages.success(request, "Application updated successfully.")
            return redirect("my_application_detail", pk=application.pk)

        messages.error(request, "Please correct the errors below.")
    else:
        form = JobApplicationForm(instance=application)

    return render(request, "jobs/application_form.html", {
        'form': form,
        'job': application.job,
        'application': application,
        'is_edit': True,
    })


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def withdraw_application(request, application_id):
    application = get_object_or_404(
        Application,
        pk=application_id,
        applicant=request.user.applicant_profile,
        status__in=ACTIVE_STATUSES,
    )

    if request.method == 'POST':
        application.update_status('withdrawn')
        messages.success(request, "Application withdrawn.")
        return redirect("my_applications")

    return render(request, "jobs/application_confirm_withdraw.html", {'application': application})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def view_my_applications(request):
    applications = Application.objects.filter(
        applicant=request.user.applicant_profile
    ).order_by('-applied_at')

    return render(request, 'jobs/my_applications.html', {'applications': applications})


@login_required(login_url='login')
def view_my_application_detail(request, pk):
    if not is_applicant(request.user):
        return render(request, "shared/access_denied.html", status=403)

    if not has_applicant_profile(request.user):
        return redirect('applicant_profile')

    application = get_object_or_404(Application, pk=pk, applicant=request.user.applicant_profile)
    return render(request, 'jobs/my_application_detail.html', {'application': application})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def accept_job_application(request, application_id):
    application = get_object_or_404(Application, pk=application_id, status__in=ACTIVE_STATUSES)
    job = application.job

    if job.created_by != request.user:
        messages.error(request, "Job this application is for isn't created by you!")
        return redirect("all_jobs_created")

    if job.post_type != 'job' or job.status != 'published' or not job.is_active:
        messages.error(request, "Job this application is for has issues!")
        return redirect("all_jobs_created")

    if not application.is_active:
        messages.error(request, "Application is no more active!")
        return redirect("all_jobs_created")

    if job.applications.filter(status='accepted').exists():
        messages.error(request, "An application for this job is already accepted!")
        return redirect("all_jobs_created")

    all_applications = job.applications.all()
    application.update_status('accepted')

    for other_application in all_applications:
        if other_application != application:
            other_application.update_status('rejected')

    job.fill_post()
    messages.success(request, "Application for the job accepted!")
    return redirect("applications_for_job", job_id=job.pk)
