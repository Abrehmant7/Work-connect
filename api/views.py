from rest_framework.views import APIView
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
    RetrieveAPIView
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from recruiter.models import(
    RepresentativeProfile,
    Company,
    Post,
    Skill
) 
from django.shortcuts import get_object_or_404

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    RepresentativeProfileSerializer,
    ApplicantProfileSerializer,
    CompanySerializer,
    JobSerializer,
    ProjectSerializer,
    SkillSerializer
)
from rest_framework.exceptions import PermissionDenied, ValidationError


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    'message': 'User registered successfully.',
                    'tokens': tokens,
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    'message': 'Login successful.',
                    'tokens': tokens,
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')

        if refresh_token is None:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )
    

class RepresentativeProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = request.user.representative_profile
        except RepresentativeProfile.DoesNotExist:
            return Response(
                {'detail': 'Representative profile does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RepresentativeProfileSerializer(profile)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        if request.user.user_type != 'representative':
            return Response(
                {'detail': 'Only representatives can create a representative profile.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if hasattr(request.user, 'representative_profile'):
            return Response(
                {'detail': 'Representative profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RepresentativeProfileSerializer(data=request.data)

        if serializer.is_valid():
            profile = serializer.save(user=request.user)

            return Response(
                RepresentativeProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request):
        profile = request.user.representative_profile
        if request.user.user_type != 'representative':
            return Response(
                {'detail': 'Only representatives can create a representative profile.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not hasattr(request.user, 'representative_profile'):
            return Response(
                {'detail': 'Representative does not have a profile.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RepresentativeProfileSerializer(profile, 
                                                     data=request.data,
                                                     partial = True)

        if serializer.is_valid():
            profile = serializer.save(user=request.user)

            return Response(
                RepresentativeProfileSerializer(profile).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    
class ApplicantProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, 'applicant_profile', None)
        if profile:
            serializer = ApplicantProfileSerializer(profile)
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'detail': "Applicant profile does not exist!"},
                status=status.HTTP_404_NOT_FOUND
            )
        
    def post(self, request):
        if request.user.user_type != "applicant":
            return Response(
                {'detail': 'Only Applicants can create an applicant profile!'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if hasattr(request.user, 'applicant_profile'):
            return Response(
                {'detail': 'Applicant profile already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ApplicantProfileSerializer(data = request.data)

        if serializer.is_valid():
            profile = serializer.save(user = request.user)
            return Response(
                ApplicantProfileSerializer(profile).data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def patch(self, request):
        profile = getattr(request.user, 'applicant_profile', None)

        if request.user.user_type != "applicant":
            return Response(
                {'detail': 'Only Applicants can create an applicant profile!'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not hasattr(request.user, 'applicant_profile'):
            return Response(
                {'detail': 'Applicant profile does not exist.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ApplicantProfileSerializer(profile,
                                                data = request.data,
                                                partial = True)

        if serializer.is_valid():
            profile = serializer.save(user = request.user)
            return Response(
                ApplicantProfileSerializer(profile).data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    

class CompaniesListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(companies, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        if request.user.user_type != "representative":
            return Response(
                {'detail': 'Only representatives can create a company.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        representative_profile = getattr(request.user, 'representative_profile', None)

        if representative_profile is None:
            return Response(
                {'detail': 'Representative profile is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        company = getattr(request.user.representative_profile, 'company', None)

        if company:
            return Response(
                {'detail': 'A company by this representative already exists!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = CompanySerializer(data = request.data)
        
        if serializer.is_valid():
            company = serializer.save()
            user_profile = get_object_or_404(RepresentativeProfile, user__pk = request.user.pk)
            user_profile.company = company
            user_profile.save()

            return Response(
                CompanySerializer(company).data,
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class CompanyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        serializer = CompanySerializer(company)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):
        company = get_object_or_404(Company, pk=pk)

        if request.user.user_type != "representative":
            return Response(
                {'detail': 'Only representatives can update company.'},
                status=status.HTTP_403_FORBIDDEN
            )

        representative_profile = getattr(request.user, 'representative_profile', None)

        if representative_profile is None:
            return Response(
                {'detail': 'Representative profile is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if representative_profile.company_id != company.id:
            return Response(
                {'detail': 'You can only update your own company.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CompanySerializer(
            company,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        company = get_object_or_404(Company, pk=pk)

        if request.user.user_type != "representative":
            return Response(
                {'detail': 'Only representatives can delete company.'},
                status=status.HTTP_403_FORBIDDEN
            )

        representative_profile = getattr(request.user, 'representative_profile', None)

        if representative_profile is None:
            return Response(
                {'detail': 'Representative profile is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if representative_profile.company_id != company.id:
            return Response(
                {'detail': 'You can only delete your own company.'},
                status=status.HTTP_403_FORBIDDEN
            )

        company.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
    
class CompanyJobsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)

        jobs = Post.objects.filter(
            company=company,
            post_type='job'
        )

        serializer = JobSerializer(jobs, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
class CompanyProjectsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)

        projects = Post.objects.filter(
            company=company,
            post_type='project'
        )

        serializer = ProjectSerializer(projects, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class SkillListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class SkillDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    

class JobListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Post.objects.filter(post_type='job')

    def perform_create(self, serializer):
        if self.request.user.user_type != 'representative':
            raise PermissionDenied('Only representatives can create jobs.')

        representative_profile = getattr(
            self.request.user,
            'representative_profile',
            None
        )

        if representative_profile is None:
            raise ValidationError('Representative profile is required.')

        if representative_profile.company is None:
            raise ValidationError('Representative must belong to a company.')

        serializer.save(
            post_type='job',
            company=representative_profile.company,
            created_by=self.request.user
        )

class JobDetailAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Post.objects.filter(post_type='job')

    def perform_update(self, serializer):
        if self.request.user.user_type != 'representative':
            raise PermissionDenied('Only representatives can update jobs.')

        representative_profile = getattr(
            self.request.user,
            'representative_profile',
            None
        )

        if representative_profile is None:
            raise ValidationError('Representative profile is required.')
        
        job = self.get_object()

        if job.created_by != self.request.user:
            raise PermissionDenied("Only the representative who created the job can update it")
        
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.user_type != 'representative':
            raise PermissionDenied('Only representatives can delete jobs.')

        representative_profile = getattr(
            self.request.user,
            'representative_profile',
            None
        )

        if representative_profile is None:
            raise ValidationError('Representative profile is required.')
        

        if instance.created_by != self.request.user:
            raise PermissionDenied("Only the representative who created the job can delete it")
        
        instance.delete_post()



# GET    /api/skills
# POST   /api/skills
# GET    /api/skills/{id}
# PATCH  /api/skills/{id}
# DELETE /api/skills/{id}

# GET    /api/jobs
# POST   /api/jobs
# GET    /api/jobs/{id}
# PATCH  /api/jobs/{id}
# DELETE /api/jobs/{id}

# POST   /api/jobs/{id}/publish
# POST   /api/jobs/{id}/close
# POST   /api/jobs/{id}/fill
# POST   /api/jobs/{id}/cancel

# GET    /api/jobs/{id}/applications
# POST   /api/jobs/{id}/applications
# GET    /api/jobs/{id}/comments
# POST   /api/jobs/{id}/comments