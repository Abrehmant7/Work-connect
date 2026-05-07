from django.db import models
from django.core.validators import (
    FileExtensionValidator, 
    MinValueValidator, 
    MaxValueValidator
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from .utils import generate_slug
from django.contrib.auth.models import AbstractUser

class TimeStampedModel(models.Model):
    """
    Abstract base class providing self-updating created and modified timestamps.
    Professional practice: Include in all models for auditing.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Company(TimeStampedModel):
    """
    Company model with proper constraints and additional business fields.
    """
    name = models.CharField(
        max_length=150, 
        unique=True,
        help_text="Official company name"
    )
    location = models.CharField(
        max_length=150,
        help_text="Headquarters location"
    )
    website = models.URLField(
        blank=True,
        help_text="Company website URL"
    )
    description = models.TextField(
        blank=True,
        help_text="Company description and mission"
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Primary industry (e.g., Technology, Healthcare)"
    )
    size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Number of employees",
        verbose_name="Company Size"
    )
    logo = models.ImageField(
        upload_to='company_logos/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Company logo image"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the company is currently active on the platform"
    )
    
    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['industry']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Professional: Add model-level validation"""
        if self.size is not None and self.size < 0:
            raise ValidationError({'size': 'Company size cannot be negative'})
    
    @property
    def active_job_count(self):
        """Professional: Useful property method"""
        return self.posts.filter(is_active=True, post_type='job').count()
    
    @property
    def active_project_count(self):
        """Professional: Useful property method"""
        return self.posts.filter(is_active=True, post_type='project').count()


class Skill(TimeStampedModel):
    """
    Skills model with categorization and normalization.
    Professional: Skills should be normalized to avoid duplicates.
    """
    CATEGORY_CHOICES = [
        ('programming', 'Programming'),
        ('design', 'Design'),
        ('business', 'Business'),
        ('marketing', 'Marketing'),
        ('data', 'Data Science'),
        ('devops', 'DevOps'),
        ('soft', 'Soft Skills'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Skill name (e.g., Python, React, Project Management)"
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        help_text="Skill category for grouping"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of the skill"
    )
    is_popular = models.BooleanField(
        default=False,
        help_text="Mark popular skills for quick selection"
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_popular']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
    
    def save(self, *args, **kwargs):
        """Professional: Normalize skill names on save"""
        self.name = self.name.strip().title()
        if(Skill.objects.filter(name = self.name)):
            raise ValidationError({'name':'skill already exists'})

        super().save(*args, **kwargs)


class CustomUser(AbstractUser):
    """
    Professional approach: Extend Django's AbstractUser for proper auth integration.
    Note: You wanted your own model, so I'm keeping it but with improvements.
    """
    USER_TYPE_CHOICES = [
        ('applicant', 'Applicant'),
        ('representative', 'Company Representative'),
        ('admin', 'Administrator'),
    ]

    email = models.EmailField(unique=True)
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='applicant'
    )
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/%Y/%m/%d/',
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['username']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} ({self.email})"
    
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    



class ApplicantProfile(TimeStampedModel):
    """
    Professional: Separate profile model for additional applicant data.
    Better than inheritance for flexibility.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='applicant_profile',
        limit_choices_to={'user_type': 'applicant'}
    )
    cv = models.FileField(
        upload_to='cvs/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
        help_text="Upload your CV (PDF or DOCX)"
    )
    summary = models.TextField(
        blank=True,
        help_text="Professional summary or bio"
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience"
    )
    skills = models.ManyToManyField(
        Skill,
        related_name="applicants",
        blank=True,
        help_text="Select your skills"
    )
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    
    # Preferences
    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Expected annual salary"
    )
    location_preference = models.CharField(max_length=150, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['experience_years']),
        ]
     
    def __str__(self):
        return f"Applicant: {self.user.first_name}"
    
    @property
    def skill_names(self):
        """Professional: Useful property for templates"""
        return list(self.skills.values_list('name', flat=True))
    
    @property
    def has_complete_profile(self):
        """Professional: Business logic property"""
        required_fields = [self.summary, self.cv]
        return all(required_fields)


class RepresentativeProfile(TimeStampedModel):
    """
    Professional: Separate profile for company representatives.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='representative_profile',
        limit_choices_to={'user_type': 'representative'}
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="representatives"
    )
    position = models.CharField(
        max_length=100,
        help_text="Position at the company (e.g., HR Manager, Tech Lead)"
    )
    department = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_primary_contact = models.BooleanField(
        default=False,
        help_text="Primary contact for the company"
    )
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['company', 'is_primary_contact'],
                condition=models.Q(is_primary_contact=True),
                name='unique_primary_contact_per_company'
            )
        ]
    
    def __str__(self):
        return f"{self.user.name} - {self.company.name}"


class Post(TimeStampedModel):
    """
    Professional: Single table inheritance pattern for posts.
    More efficient than abstract base class for queries.
    """
    POST_TYPE_CHOICES = [
        ('job', 'Job Position'),
        ('project', 'Project'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
        ('filled', 'Filled/Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        db_index=True
    )
    title = models.CharField(
        max_length=250,
        help_text="Title of the job or project"
    )
    description = models.TextField(
        help_text="Detailed description"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    
    # Polymorphic fields - only one will be used based on post_type
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Annual salary for jobs"
    )
    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Total budget for projects"
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps (inherits created_at, updated_at from TimeStampedModel)
    published_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Relationships
    skills_required = models.ManyToManyField(
        Skill,
        related_name="posts",
        blank=True
    )
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="created_posts"
    )
    slug = models.SlugField(blank=True, null=True)
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post_type', 'status', 'is_active']),
            models.Index(fields=['company', 'status']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_post_type_display()})"
    
    def clean(self):
        """Professional: Model-level validation"""
        if self.post_type == 'job' and not self.salary:
            raise ValidationError({'salary': 'Job posts must have a salary'})
        if self.post_type == 'project' and not self.budget:
            raise ValidationError({'budget': 'Project posts must have a budget'})
        
        # Only one of salary/budget should be set
        if self.salary and self.budget:
            raise ValidationError('A post cannot have both salary and budget')
    
    def save(self, *args, **kwargs):
        """Professional: Business logic in save method"""
        is_new = self.pk is None
        
        # Set published_at if status changes to published
        if self.status == 'published' and (is_new or self.status != 'published'):
            self.published_at = timezone.now()
        
        # Set closed_at if status changes to closed/filled/cancelled
        if self.status in ['closed', 'filled', 'cancelled'] and \
           (is_new or self.status not in ['closed', 'filled', 'cancelled']):
            self.closed_at = timezone.now()
            self.is_active = False

        if not self.slug:
            self.slug = generate_slug(self.title)
        
        super().save(*args, **kwargs)
    
    @property
    def is_open(self):
        """Professional: Useful property for business logic"""
        return self.status == 'published' and self.is_active
    
    @property
    def display_amount(self):
        """Professional: Dynamic property based on post type"""
        if self.post_type == 'job':
            return f"${self.salary:,.2f}/year" if self.salary else "Negotiable"
        elif self.post_type == 'project':
            return f"${self.budget:,.2f} budget" if self.budget else "Budget not specified"
        return ""
    
    def close_post(self):
        """Professional: Model method for business operation"""
        self.status = 'closed'
        self.closed_at = timezone.now()
        self.is_active = False
        self.save()

    def fill_post(self):
        """Professional: Model method for business operation"""
        self.status = 'filled'
        self.closed_at = timezone.now()
        self.is_active = False
        self.save()


class Proposal(TimeStampedModel):
    """
    Professional: Through model for project bids with proper constraints.
    """
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('reviewing', 'Under Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Proposal Amount",
        help_text="Bid amount for the project"
    )
    description = models.TextField(
        help_text="Detailed proposal description"
    )
    applicant = models.ForeignKey(
        ApplicantProfile,
        on_delete=models.CASCADE,
        related_name="proposals"
    )
    project = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="proposals",
        limit_choices_to={'post_type': 'project', 'status': 'published'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted',
        db_index=True
    )
    cover_letter = models.FileField(
        upload_to='proposals/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text="Optional cover letter (PDF)"
    )
    estimated_duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Estimated duration in days"
    )
    
    # Metadata
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        RepresentativeProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_proposals"
    )
    
    class Meta:
        ordering = ['amount', '-submitted_at']
        constraints = [
            models.UniqueConstraint(
                fields=['applicant', 'project'],
                name='unique_proposal_per_applicant_project',
                violation_error_message="You have already submitted a proposal for this project"
            ),
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='proposal_amount_non_negative'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'submitted_at']),
            models.Index(fields=['project', 'status']),
        ]
    
    def __str__(self):
        return f"Proposal by {self.applicant.user.name} for {self.project.title}"
    
    def clean(self):
        """Professional: Validate proposal amount doesn't exceed project budget"""
        if self.amount and self.project.budget and self.amount > self.project.budget:
            raise ValidationError({
                'amount': f'Proposal amount (${self.amount}) cannot exceed project budget (${self.project.budget})'
            })
    
    def accept(self, reviewed_by):
        """Professional: Business logic method"""
        self.status = 'accepted'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.save()
    
    def reject(self, reviewed_by):
        """Professional: Business logic method"""
        self.status = 'rejected'
        self.reviewed_by = reviewed_by
        self.reviewed_at = timezone.now()
        self.save()
    
    @property
    def is_pending(self):
        return self.status in ['submitted', 'reviewing']


class Comment(TimeStampedModel):
    """
    Professional: Comments system with threading capability.
    """
    comment_text = models.TextField(
        help_text="Comment content"
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )
    is_edited = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        username = self.user.name if self.user else "Deleted User"
        return f"Comment by {username} on {self.post.title[:30]}..."
    
    @property
    def is_reply(self):
        return self.parent_comment is not None
    
    def edit_comment(self, new_text):
        """Professional: Edit comment with tracking"""
        self.comment_text = new_text
        self.is_edited = True
        self.save()


class Application(TimeStampedModel):
    """
    Professional: Job applications model (you were missing this!).
    """
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
        ('accepted', 'Accepted'),
    ]
    
    applicant = models.ForeignKey(
        ApplicantProfile,
        on_delete=models.CASCADE,
        related_name="applications"
    )
    job = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={'post_type': 'job', 'status': 'published'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='applied',
        db_index=True
    )
    cover_letter = models.TextField(
        blank=True,
        help_text="Cover letter for the job application"
    )
    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Your expected salary for this position"
    )
    
    # Metadata
    applied_at = models.DateTimeField(auto_now_add=True)
    status_changed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields=['applicant', 'job'],
                name='unique_application_per_applicant_job'
            )
        ]
        indexes = [
            models.Index(fields=['status', 'applied_at']),
            models.Index(fields=['job', 'status']),
        ]
    
    def __str__(self):
        return f"{self.applicant.user.first_name} → {self.job.title}"
    
    @property
    def is_active(self):
        return self.status in ['applied', 'reviewing']
    
    def is_accepted(self):
        return self.status == 'accepted'
    
    def update_status(self, new_status):
        """Professional: Update application status"""
        self.status = new_status
        self.status_changed_at = timezone.now()
        self.save()


