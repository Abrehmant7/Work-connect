from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    RegisterAPIView,
    LoginAPIView,
    MeAPIView,
    LogoutAPIView,
    RepresentativeProfileAPIView,
    ApplicantProfileAPIView,
    CompaniesListAPIView,
    CompanyDetailAPIView,
    CompanyJobsAPIView,
    CompanyProjectsAPIView,
    SkillListCreateAPIView,
    SkillDetailAPIView,
    JobListCreateAPIView,
    JobDetailAPIView
)

router = DefaultRouter()

urlpatterns = [
    path('auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/me/', MeAPIView.as_view(), name='api_me'),
    path('auth/logout/', LogoutAPIView.as_view(), name='api_logout'),

    path('representative-profiles/me/', RepresentativeProfileAPIView.as_view(), name='representative_profile_me'),
    path('applicant-profiles/me/', ApplicantProfileAPIView.as_view(), name='applicant_profile_me'),

    path('companies/', CompaniesListAPIView.as_view(), name='companies_list'),
    path('companies/<int:pk>/', CompanyDetailAPIView.as_view(), name='company_detail'),
    path('companies/<int:pk>/jobs/', CompanyJobsAPIView.as_view(), name='company_jobs' ),
    path('companies/<int:pk>/projects/', CompanyProjectsAPIView.as_view(), name='company_projects' ),

    path('skills/', SkillListCreateAPIView.as_view(), name='skills_list_create'),
    path('skills/<int:pk>/', SkillDetailAPIView.as_view(), name='skill_detail'),

    path('jobs/', JobListCreateAPIView.as_view(), name='jobs_list'),
    path('jobs/<int:pk>/', JobDetailAPIView.as_view(), name='job_detail'),


    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

urlpatterns += router.urls