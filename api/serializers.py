from rest_framework import serializers
from recruiter.models import (
    CustomUser,
    ApplicantProfile,
    RepresentativeProfile,
    Company,
    Skill,
    Post,
    Application,
    Proposal,
    Comment
)
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_type',
            'profile_picture',
            'password',
            'password2',
        ]
        read_only_fields = ['id']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                'password': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')

        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(
            password=password,
            **validated_data
        )

        return user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get('identifier')
        password = attrs.get('password')

        user = CustomUser.objects.filter(email=identifier).first()

        if user is None:
            user = CustomUser.objects.filter(username=identifier).first()

        if user is None:
            raise serializers.ValidationError('Invalid login credentials.')

        authenticated_user = authenticate(
            username=user.username,
            password=password
        )

        if authenticated_user is None:
            raise serializers.ValidationError('Invalid login credentials.')

        if not authenticated_user.is_active:
            raise serializers.ValidationError('This account is disabled.')

        attrs['user'] = authenticated_user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'user_type',
            'profile_picture',
        ]
        read_only_fields = ['id', 'username', 'email', 'user_type']



class RepresentativeProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepresentativeProfile
        fields = [
            'position',
            'department',
            'phone'
        ]

class ApplicantProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantProfile
        fields = [
            'cv',
            'summary',
            'experience_years',
            'skills',
            'linkedin_url',
            'github_url',
            'portfolio_url',
            'location_preference',
            'expected_salary',
        ]

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'name',
            'location',
            'website',
            'description',
            'industry',
            'size',
            'logo'
        ]
        


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'salary',
            'status',
            'is_active',
            'is_featured',
            'skills_required',
            'company',
            'created_by',
            'post_type',
            'published_at',
            'closed_at',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'company',
            'created_by',
            'post_type',
            'is_active',
            'is_featured',
            'published_at',
            'closed_at',
            'created_at',
        ]

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'description',
            'budget',
            'status',
            'is_active',
            'is_featured',
            'published_at',
            'closed_at',
            'created_at',
        ]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            'id',
            'name',
            'category',
            'description',
            'is_popular',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']