from django.urls import path, URLPattern
from . import views

urlpatterns = [
    path("", views.index, name = "home"),
    # path("add_form/", views.job_form, name = "add_form"),
    # path("add_job/", views.add_job, name = "add_job"),
    path("<slug:slug>/detail/", views.view_job, name = "view_job"),
    

    path("sign_up", views.signUp, name="sign_up"),
    path("login", views.logIn, name="login"),
    path("logout", views.logOut, name="logout"),

    path("representative_profile", views.complete_representative_profile, name="representative_profile"),
    path("applicant_profile", views.complete_applicant_profile, name="applicant_profile"),

    path("company_creation", views.create_company, name="company_creation"),
    path("add_job", views.addJob, name="add_job"),

    path("skill_redirect", views.skillRedirect, name="skill_redirect"),
    path("add_skill", views.addSkill, name="add_skill"),

    path("<slug:slug>/detail", views.view_job, name='view_job'),
    path("<int:job_pk>", views.apply_to_job, name="job_application"),
    path("my_applications", views.view_my_applications, name="my_applications"),
    path("application_detail/<int:pk>", views.view_my_application_detail, name="my_application_detail")
]