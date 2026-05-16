from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from recruiter.forms import ProjectForm, ProposalForm
from recruiter.models import Post, Proposal
from .common import (
    ACTIVE_PROPOSAL_STATUSES,
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
def addProject(request):
    if not request.user.representative_profile.company:
        messages.info(request, "You have to register a company first!")
        return redirect('company_creation')

    saved_post_data = request.session.get('saved_post_form_data', {})

    if request.method == 'POST':
        form = ProjectForm(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            project.post_type = 'project'
            project.created_by = request.user
            project.status = 'published'
            project.company = request.user.representative_profile.company
            project.published_at = timezone.now()
            project.save()
            form.save_m2m()

            request.session.pop('saved_post_form_data', None)
            request.session.pop('skill_return_url', None)

            messages.success(request, "Project created successfully!")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm(saved_post_data) if saved_post_data else ProjectForm()

    return render(request, "projects/project_form.html", {'form': form})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def edit_project(request, project_id):
    project = get_object_or_404(Post, pk=project_id, post_type='project', created_by=request.user)

    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)

        if form.is_valid():
            project = form.save(commit=False)
            project.post_type = 'project'
            project.created_by = request.user
            project.company = request.user.representative_profile.company
            project.save()
            form.save_m2m()
            messages.success(request, "Project updated successfully!")
            return redirect("proposals_for_project", project_id=project.pk)

        messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/project_form.html", {
        'form': form,
        'project': project,
        'is_edit': True,
    })


@login_required(login_url='login')
@representative_required
@representative_profile_required
def delete_project(request, project_id):
    project = get_object_or_404(Post, pk=project_id, post_type='project', created_by=request.user)

    if request.method == 'POST':
        project.status = 'cancelled'
        project.is_active = False
        project.closed_at = timezone.now()
        project.save()
        messages.success(request, "Project deleted successfully.")
        return redirect("all_projects_created")

    return render(request, "projects/project_confirm_delete.html", {'project': project})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def view_all_projects_created(request):
    projects = Post.objects.filter(
        post_type='project',
        created_by=request.user,
        status__in=['filled', 'published', 'cancelled', 'closed'],
    ).order_by('-created_at')

    return render(request, 'projects/all_projects_created.html', {'projects': projects})


@login_required(login_url='login')
def view_proposals_for_project(request, project_id):
    if not is_representative(request.user):
        messages.error(request, "You are not allowed to access this page!")
        return redirect("all_projects_created")

    profile = getattr(request.user, 'representative_profile', None)

    if not profile:
        messages.error(request, "You have to create profile first!")
        return redirect("representative_profile")

    project = get_object_or_404(Post, post_type='project', pk=project_id, created_by=request.user)
    accepted_proposal = project.proposals.filter(status='accepted').first()
    proposals = [] if accepted_proposal else project.proposals.all()

    return render(request, "projects/proposals_for_project.html", {
        'proposals': proposals,
        'accepted_proposal': accepted_proposal,
        'project': project,
    })


@login_required(login_url='login')
@representative_required
@representative_profile_required
def view_proposal_detail(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id, project__created_by=request.user)
    return render(request, 'projects/proposal_detail.html', {'proposal': proposal})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def submit_project_proposal(request, project_pk):
    profile = getattr(request.user, "applicant_profile", None)
    project = get_object_or_404(Post, post_type='project', pk=project_pk, status='published', is_active=True)

    if Proposal.objects.filter(applicant=profile, project=project).exists():
        messages.error(request, "You already have a proposal for this project!")
        return redirect('view_project', slug=project.slug)

    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES, project=project)

        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.applicant = profile
            proposal.project = project
            proposal.status = 'submitted'
            proposal.save()
            messages.success(request, "Proposal submitted successfully.")
            return redirect("/")

        messages.error(request, "Please correct the errors below.")
    else:
        form = ProposalForm(project=project)

    return render(request, "projects/proposal_form.html", {'form': form, 'project': project})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def edit_proposal(request, proposal_id):
    proposal = get_object_or_404(
        Proposal,
        pk=proposal_id,
        applicant=request.user.applicant_profile,
        status__in=ACTIVE_PROPOSAL_STATUSES,
    )

    if request.method == 'POST':
        form = ProposalForm(request.POST, request.FILES, instance=proposal, project=proposal.project)

        if form.is_valid():
            updated_proposal = form.save(commit=False)
            updated_proposal.project = proposal.project
            updated_proposal.applicant = request.user.applicant_profile
            updated_proposal.save()
            messages.success(request, "Proposal updated successfully.")
            return redirect("my_proposal_detail", pk=proposal.pk)

        messages.error(request, "Please correct the errors below.")
    else:
        form = ProposalForm(instance=proposal, project=proposal.project)

    return render(request, "projects/proposal_form.html", {
        'form': form,
        'project': proposal.project,
        'proposal': proposal,
        'is_edit': True,
    })


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def withdraw_proposal(request, proposal_id):
    proposal = get_object_or_404(
        Proposal,
        pk=proposal_id,
        applicant=request.user.applicant_profile,
        status__in=ACTIVE_PROPOSAL_STATUSES,
    )

    if request.method == 'POST':
        proposal.status = 'withdrawn'
        proposal.save()
        messages.success(request, "Proposal withdrawn.")
        return redirect("my_proposals")

    return render(request, "projects/proposal_confirm_withdraw.html", {'proposal': proposal})


@login_required(login_url='login')
@applicant_required
@applicant_profile_required
def view_my_proposals(request):
    proposals = Proposal.objects.filter(
        applicant=request.user.applicant_profile
    ).order_by('-submitted_at')

    return render(request, 'projects/my_proposals.html', {'proposals': proposals})


@login_required(login_url='login')
def view_my_proposal_detail(request, pk):
    if not is_applicant(request.user):
        return render(request, "shared/access_denied.html", status=403)

    if not has_applicant_profile(request.user):
        return redirect('applicant_profile')

    proposal = get_object_or_404(Proposal, pk=pk, applicant=request.user.applicant_profile)
    return render(request, 'projects/my_proposal_detail.html', {'proposal': proposal})


@login_required(login_url='login')
@representative_required
@representative_profile_required
def accept_project_proposal(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id, status__in=ACTIVE_PROPOSAL_STATUSES)
    project = proposal.project

    if project.created_by != request.user:
        messages.error(request, "Project this proposal is for isn't created by you!")
        return redirect("all_projects_created")

    if project.post_type != 'project' or project.status != 'published' or not project.is_active:
        messages.error(request, "Project this proposal is for has issues!")
        return redirect("all_projects_created")

    if not proposal.is_pending:
        messages.error(request, "Proposal is no more active!")
        return redirect("all_projects_created")

    if project.proposals.filter(status='accepted').exists():
        messages.error(request, "A proposal for this project is already accepted!")
        return redirect("all_projects_created")

    all_proposals = project.proposals.all()
    proposal.accept(request.user.representative_profile)

    for other_proposal in all_proposals:
        if other_proposal != proposal:
            other_proposal.reject(request.user.representative_profile)

    project.fill_post()
    messages.success(request, "Proposal for the project accepted!")
    return redirect("proposals_for_project", project_id=project.pk)
