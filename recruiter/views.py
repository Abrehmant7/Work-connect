from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Post, Skill, CustomUser, ApplicantProfile, RepresentativeProfile, Proposal,Application
# views.py
import logging

from django.shortcuts import render, redirect
from .forms import JobForm, CustomUserCreationForm, SkillForm, RepresentitativeProfileForm, CompanyForm, ApplicantProfileForm, JobApplicationForm
from django.urls import reverse
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponseBadRequest

logger = logging.getLogger(__name__)

# Create your views here.

######################### list for statuses that make a job application valid###########################
ACTIVE_STATUSES = ['applied', 'reviewing', 'shortlisted', 'interviewing']

def is_representative(user):
    return user.user_type == 'representative'

def is_applicant(user):
    return user.user_type == 'applicant'

def has_applicant_profile(user):
    return hasattr(user, 'applicant_profile')

def has_representative_profile(user):
    return hasattr(user, 'representative_profile')

@login_required(login_url='login')
def index(request):
    jobs = Post.objects.filter(post_type = 'job',
                               status = 'published',
                               is_active = True).order_by('-created_at')
    return render(request, "recruiter/dashboard.html", {'jobs':jobs})

@login_required(login_url='login')
def view_job(request, slug):
    job = get_object_or_404(Post, slug = slug,
                            post_type = 'job',
                            status = 'published',
                            is_active = True)
    return render(request, "recruiter/job_detail.html", {"job" : job})


def signUp(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.user_type == 'representative':
                return redirect("representative_profile")
            elif user.user_type == 'applicant':
                return redirect("applicant_profile")
    
    else:
        form = CustomUserCreationForm()

    return render(request, "recruiter/sign_up.html", {'form' : form})


def logIn(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)

            if user.user_type == 'applicant':
                if not hasattr(user, 'applicant_profile'):
                    redirect("applicant_profile")
                
            elif user.user_type == "representative":
                if not hasattr(user, 'representative_profile'):
                    redirect("representative_profile")

            return redirect("/")
        
        else:
            return render(request, 'recruiter/log_in.html', {"error" : "invalid credentials"})
        
    return render(request, "recruiter/log_in.html")

def logOut(request):
    logout(request)

    return redirect('login')


@login_required(login_url='login')
def complete_representative_profile(request):
    if has_representative_profile(request.user):
        redirect('/')

    if request.method == 'POST':
        form = RepresentitativeProfileForm(request.POST or None)

        if form.is_valid():
            profile =  form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("/")
        
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = RepresentitativeProfileForm()

    return render(request, "recruiter/representative_profile.html", {'form':form})


@login_required(login_url='login')
def complete_applicant_profile(request):
    if has_applicant_profile(request.user):
        return redirect("/")
    
    if request.method == 'POST':
        form = ApplicantProfileForm(request.POST or None, request.FILES)

        if form.is_valid():
            profile =  form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("/")
        
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = ApplicantProfileForm()

    return render(request, "recruiter/applicant_profile.html", {'form':form})



@login_required(login_url='login')
def create_company(request):
    if not is_representative(request.user):
        return HttpResponse("You are not allowed to view this page!")
    
    if request.user.representative_profile.company is not None:
        return redirect('/')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST or None)

        if form.is_valid():
            company = form.save()
            user_profile = get_object_or_404(RepresentativeProfile, user__pk = request.user.pk)
            user_profile.company = company
            user_profile.save()
            messages.success(request, "Company created successfully!")
            return redirect("/")
        
        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = CompanyForm()

    return render(request, 'recruiter/companyForm.html', {'form' : form})


@login_required(login_url='login')
def addJob(request):
    if not is_representative(request.user):
        return HttpResponse("You are not allowed to access this page!")
    
    profile = has_representative_profile(request.user)
    if not profile or not request.user.representative_profile.company:
        return redirect("company_creation")
    
    saved_post_data = request.session.get('saved_post_form_data', {})

    if request.method == 'POST':
        form = JobForm(request.POST)

        if form.is_valid():
            job_post = form.save(commit=False)
            job_post.post_type = 'job'
            job_post.created_by = request.user
            job_post.status = 'published'
            job_post.company = request.user.representative_profile.company
            job_post.save()
            form.save_m2m()


            if 'saved_post_form_data' in request.session:
                del request.session['saved_post_form_data']
            messages.success(request, "Post created successfully!")
            return redirect("/")
        
        else:
            messages.error(request, "Please correct the errors below.")
            print(form.errors)
        
    else:
        if saved_post_data:
            form = JobForm(saved_post_data)
        else:
            form = JobForm()

    return render(request, "recruiter/jobForm.html", {'form' : form})

@login_required(login_url='login')
def skillRedirect(request):
    if request.method == 'POST':
            
            # Get the main form data from the hidden field
            # This is the ONLY place we use a hidden field
        main_form_data = request.POST.get('main_form_data', '')
            
        if main_form_data:
                # Parse the URL-encoded form data
            from urllib.parse import parse_qs
            parsed_data = parse_qs(main_form_data)
                
                # Convert to format suitable for JobForm
                # parse_qs returns { 'title': ['value'], 'description': ['value'] }
            cleaned_data = {}
            for key, value_list in parsed_data.items():
                cleaned_data[key] = value_list[0] if len(value_list) == 1 else value_list
                
                # Save to session so addPost can access it
            request.session['saved_post_form_data'] = cleaned_data
            
        return redirect('add_skill')
    
    return redirect('add_job')

@login_required(login_url='login')
def addSkill(request):
    if not is_representative(request.user):
        return HttpResponse("You are not allowed to access this page!")
    
    if not request.user.representative_profile.company:
        return redirect("company_creation")
    
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f"Skill '{skill.name}' added successfully!")
            return redirect('add_job')
        else:
            messages.error(request, "Please correct the errors below.")
    
    else:
        form = SkillForm()

    return render(request, "recruiter/add_skill.html", { 'form' : form })


######################### view jobs created by the representative  ###################################
@login_required(login_url='login')
def view_all_jobs_created(request):
    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("/")
    
    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.error(request, "You have to create profile first!")
        return redirect("representative_profile")
    
    jobs = Post.objects.filter(post_type = 'job' , created_by = request.user, status__in = ['filled', 'published']).order_by('-created_at')

    return render(request, 'recruiter/all_jobs_created.html', {'jobs':jobs})


@login_required(login_url='login')
def view_applications_for_job(request, job_id):

    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("all_jobs_created")
    
    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.error(request, "You have to create profile first!")
        return redirect("representative_profile")

    job = get_object_or_404(Post, post_type = 'job', pk = job_id, created_by = request.user)

    # Get the first accepted application (if any)
    accepted_application = job.applications.filter(status='accepted').first()
    
    # If there's an accepted application, show only that one
    # Otherwise show all applications
    if accepted_application:
        applications = []  # Don't show other applications
    else:
        applications = job.applications.all()


    return render(request, "recruiter/applications_for_job.html", {'applications':applications,'accepted_application':accepted_application, 'job':job})


@login_required(login_url='login')
def view_application_detail(request, application_id):

    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("all_jobs_created")
    
    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.error(request, "You have to create profile first!")
        return redirect("representative_profile")
    
    # previously, any representative can view this application (data leak)
    # application = get_object_or_404(Application, pk = application_id)

    application = get_object_or_404(Application, pk = application_id, job__created_by = request.user)

    return render(request, 'recruiter/application_detail.html', {'application':application})


######################################  Job Application functions   ############################################

@login_required(login_url='login')
def apply_to_job(request, job_pk):

    if not is_applicant(request.user):
        return HttpResponse("Not allowed to view this page")
    
    # use helper
    profile = request.user.applicant_profile

    if not has_applicant_profile(request.user):
        return redirect('applicant_profile')
    
    job = get_object_or_404(Post, post_type = 'job', pk = job_pk, status = 'published', is_active = True)
    
    prev_applications = Application.objects.filter(applicant = profile, job = job).exists()

    if prev_applications:
        messages.error(request, "You already have an application for this job!")
        return redirect('view_job', slug = job.slug)


    if request.method == 'POST':
        form = JobApplicationForm(request.POST or None)

        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = profile
            application.job = job
            application.status = 'applied'
            application.save()
            messages.success(request, "applied for the job successfully")
            return redirect("/")

        else:
            messages.error(request, "Please correct the errors below.")

    else:
        form = JobApplicationForm()

    return render(request, "recruiter/application_form.html", {'form':form, 'job':job})


@login_required(login_url='login')
def view_my_applications(request):
    if not is_applicant(request.user):
        return HttpResponse("you are not allowed to view this page")
    
    if not has_applicant_profile(request.user):
        return redirect('applicant_profile')
    
    
    applications = Application.objects.filter(applicant = request.user.applicant_profile).order_by('-applied_at')

    return render(request, 'recruiter/my_applications.html', {'applications':applications})


@login_required(login_url='login')
def view_my_application_detail(request, pk):
    if not is_applicant(request.user):
        return HttpResponse("you are not allowed to view this page")
    
    if not has_applicant_profile(request.user):
        return redirect('applicant_profile')
    
    
    application = get_object_or_404(Application, pk = pk, applicant = request.user.applicant_profile )

    
    return render(request, 'applicant/application_detail.html', {'application':application})



@login_required(login_url='login')
def accept_job_application(request, application_id):

    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("/")

    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.info(request, "You don't have a profile!")
        return redirect("representative_profile")
    
    application = get_object_or_404(Application, pk = application_id, status__in = ACTIVE_STATUSES)

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
    
    all_applications = job.applications.all()

    # previously, performance improvement
    # for a in all_applications:
    #     if a.is_accepted():
    #         messages.error(request, "An application for this job is already accepted!")
    #         return redirect("all_jobs_created")
        
    if job.applications.filter(status='accepted').exists():
        messages.error(request, "An application for this job is already accepted!")
        return redirect("all_jobs_created")
        
    application.update_status('accepted')

    for a in all_applications:
        if a == application:
            continue
        else:
            a.update_status('rejected')

    job.fill_post()

    messages.success(request, "Application for the job accepted!")
    return redirect("applications_for_job", job_id = job.pk)



# def job_form(request):
#     """
#     Render the job creation form. Skills are passed so the template can render
#     checkboxes or a multi-select.
#     """
#     skills_available = Skill.objects.all().order_by("skill_name")
#     return render(request, "recruiter/add_form.html", {"skills_available": skills_available})


# def add_job(request):
#     """
#     Handle POST from job_form. Validates input, creates Job and links skills.
#     Uses a DB transaction so job + m2m changes are atomic.
#     Returns to /recruiter/ (same behavior as your original code) but with messages.
#     """
#     if request.method != "POST":
#         # Bad request if not POST; you can redirect instead if preferred.
#         return HttpResponseBadRequest("Invalid request method")

#     # safely get values (no KeyError)
#     job_title = request.POST.get("job_title", "").strip()
#     job_description = request.POST.get("job_description", "").strip()
#     skills_required = request.POST.getlist("skills_required")  # expected list of skill ids (strings)

#     errors = {}

#     # Basic validation
#     if not job_title:
#         errors["job_title"] = "Job title is required."
#     if not job_description:
#         errors["job_description"] = "Job description is required."

#     if errors:
#         # Re-render the form with errors and previously selected values
#         skills_available = Skill.objects.all().order_by("skill_name")
#         context = {
#             "skills_available": skills_available,
#             "errors": errors,
#             "prefill": {"job_title": job_title, "job_description": job_description, "skills_required": skills_required},
#         }
#         return render(request, "recruiter/add_form.html", context)

#     # Turn skill ids into integers safely and fetch Skill queryset
#     skill_ids = []
#     for s in skills_required:
#         try:
#             skill_ids.append(int(s))
#         except (ValueError, TypeError):
#             # skip invalid ids
#             logger.warning("Invalid skill id received: %r", s)

#     try:
#         with transaction.atomic():
#             job = Job.objects.create(
#                 job_title=job_title,
#                 job_description=job_description,
#                 post_date=timezone.now(),
#             )

#             if skill_ids:
#                 skill_qs = Skill.objects.filter(pk__in=skill_ids)
#                 # add accepts either model instances or ids; using instances is explicit:
#                 # If no skill matches the provided ids, it simply won't add any.
#                 if skill_qs.exists():
#                     job.skills_required.add(*skill_qs)

#         messages.success(request, "Job posted successfully.")
#         # keep original redirect path; switch to reverse('recruiter:dashboard') if you have a named URL
#         return redirect("/recruiter/")

#     except IntegrityError as e:
#         # Database constraint error
#         logger.exception("Database error while creating job")
#         messages.error(request, "A database error occurred. Please try again.")
#     except Exception as e:
#         # Catch-all: log for debugging and show user-friendly message
#         logger.exception("Unexpected error while creating job")
#         messages.error(request, "An unexpected error occurred. Please contact support.")

#     # If we got here an error happened — re-render form with previous input
#     skills_available = Skill.objects.all().order_by("skill_name")
#     context = {
#         "skills_available": skills_available,
#         "prefill": {"job_title": job_title, "job_description": job_description, "skills_required": skills_required},
#     }
#     return render(request, "recruiter/add_form.html", context)