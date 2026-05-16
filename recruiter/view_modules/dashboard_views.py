from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from recruiter.models import Post


@login_required(login_url='login')
def index(request):
    get_params = request.GET.copy()
    searched = request.GET.get('q', '')
    category = request.GET.get('category', '')

    if searched or category:
        jobs = Post.objects.filter(
            post_type='job',
            status='published',
            title__icontains=searched,
            skills_required__category__icontains=category,
            is_active=True,
        ).distinct().order_by('-created_at')
    else:
        jobs = Post.objects.filter(
            post_type='job',
            status='published',
            is_active=True,
        ).order_by('-created_at')

    projects = Post.objects.filter(
        post_type='project',
        status='published',
        is_active=True,
    ).order_by('-created_at')

    jobs_created = Post.objects.filter(
        post_type="job",
        status='published',
        is_active=True,
        created_by=request.user,
    )

    projects_created = Post.objects.filter(
        post_type="project",
        status='published',
        is_active=True,
        created_by=request.user,
    )

    paginator = Paginator(jobs, 4)
    page = request.GET.get('page')
    page_object = paginator.get_page(page)

    if 'page' in get_params:
        get_params.pop('page')

    if request.user.user_type == 'applicant':
        context = {
            'page_object': page_object,
            'projects': projects,
            'query_params': get_params.urlencode(),
        }
        return render(request, "dashboard/applicant_dashboard.html", context)

    context = {'jobs': jobs_created, 'projects': projects_created}
    return render(request, "dashboard/representative_dashboard.html", context)


@login_required(login_url='login')
def view_job(request, slug):
    job = get_object_or_404(
        Post,
        slug=slug,
        post_type='job',
        status='published',
        is_active=True,
    )
    return render(request, "jobs/job_detail.html", {"job": job})


@login_required(login_url='login')
def view_project(request, slug):
    project = get_object_or_404(
        Post,
        slug=slug,
        post_type='project',
        status='published',
        is_active=True,
    )
    return render(request, "projects/project_detail.html", {"project": project})
