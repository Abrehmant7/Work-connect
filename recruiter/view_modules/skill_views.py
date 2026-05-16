from urllib.parse import parse_qs

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from recruiter.forms import SkillForm
from .common import representative_profile_required, representative_required


@login_required(login_url='login')
def skillRedirect(request):
    if request.method == 'POST':
        main_form_data = request.POST.get('main_form_data', '')
        return_url = request.POST.get('next', 'add_job')
        request.session['skill_return_url'] = return_url

        if main_form_data:
            parsed_data = parse_qs(main_form_data)
            cleaned_data = {}
            for key, value_list in parsed_data.items():
                cleaned_data[key] = value_list[0] if len(value_list) == 1 else value_list

            request.session['saved_post_form_data'] = cleaned_data

        return redirect('add_skill')

    return redirect('add_job')


@login_required(login_url='login')
@representative_required
@representative_profile_required
def addSkill(request):
    if not request.user.representative_profile.company:
        return redirect("company_creation")

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save()
            messages.success(request, f"Skill '{skill.name}' added successfully!")
            return_url = request.session.get('skill_return_url', 'add_job')
            if 'add_project' in return_url:
                return redirect('add_project')
            return redirect('add_job')

        messages.error(request, "Please correct the errors below.")
    else:
        form = SkillForm()

    return render(request, "skills/add_skill.html", {'form': form})
