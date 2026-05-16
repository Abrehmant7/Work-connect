from django.urls import path, URLPattern
from . import views

urlpatterns = [
    path("", views.index, name = "home"),
    # path("add_form/", views.job_form, name = "add_form"),
    # path("add_job/", views.add_job, name = "add_job"),
    path("<slug:slug>/detail/", views.view_job, name = "view_job"),
    path("project/<slug:slug>/detail/", views.view_project, name = "view_project"),
    

    path("sign_up", views.signUp, name="sign_up"),
    path("login", views.logIn, name="login"),
    path("logout", views.logOut, name="logout"),

    path("representative_profile", views.complete_representative_profile, name="representative_profile"),
    path("applicant_profile", views.complete_applicant_profile, name="applicant_profile"),

    path("company_creation", views.create_company, name="company_creation"),
    path("add_job", views.addJob, name="add_job"),
    path("edit_job/<int:job_id>", views.edit_job, name="edit_job"),
    path("delete_job/<int:job_id>", views.delete_job, name="delete_job"),
    path("all_jobs_created", views.view_all_jobs_created, name="all_jobs_created"),
    path("applications_for_job/<int:job_id>", views.view_applications_for_job, name="applications_for_job"),
    path("application_detail/<int:application_id>", views.view_application_detail, name="application_detail"),
    path("accept_job_application/<int:application_id>", views.accept_job_application, name="accept_job_application"),

    path("add_project", views.addProject, name="add_project"),
    path("edit_project/<int:project_id>", views.edit_project, name="edit_project"),
    path("delete_project/<int:project_id>", views.delete_project, name="delete_project"),
    path("all_projects_created", views.view_all_projects_created, name="all_projects_created"),
    path("proposals_for_project/<int:project_id>", views.view_proposals_for_project, name="proposals_for_project"),
    path("proposal_detail/<int:proposal_id>", views.view_proposal_detail, name="proposal_detail"),
    path("accept_project_proposal/<int:proposal_id>", views.accept_project_proposal, name="accept_project_proposal"),

    path("skill_redirect", views.skillRedirect, name="skill_redirect"),
    path("add_skill", views.addSkill, name="add_skill"),

    path("<slug:slug>/detail", views.view_job, name='view_job'),
    path("<int:job_pk>", views.apply_to_job, name="job_application"),
    path("edit_application/<int:application_id>", views.edit_application, name="edit_application"),
    path("withdraw_application/<int:application_id>", views.withdraw_application, name="withdraw_application"),
    path("project_application/<int:project_pk>", views.submit_project_proposal, name="project_proposal"),
    path("edit_proposal/<int:proposal_id>", views.edit_proposal, name="edit_proposal"),
    path("withdraw_proposal/<int:proposal_id>", views.withdraw_proposal, name="withdraw_proposal"),
    path("my_applications", views.view_my_applications, name="my_applications"),
    path("my_application_detail/<int:pk>", views.view_my_application_detail, name="my_application_detail"),
    path("my_proposals", views.view_my_proposals, name="my_proposals"),
    path("my_proposal_detail/<int:pk>", views.view_my_proposal_detail, name="my_proposal_detail")
]
