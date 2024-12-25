from django.db import models
from django.contrib.auth.models import User
from Accounts.models import Skill, UserProfile
from DashboardPages.models import Job, JobListing
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class SkillVector(models.Model):
    """Stores vectorized representations of skills for efficient matching"""
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    vector = models.JSONField()  # Store word embedding vector
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vector for {self.skill.name}"

class CandidateVector(models.Model):
    """Stores pre-computed candidate vectors for faster matching"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skill_vector = models.JSONField()  # Aggregated skill vectors
    experience_vector = models.JSONField()  # Vector representing experience
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vector for {self.user.username}"
    
    def compute_similarity(self, job_vector):
        """Compute similarity score between candidate and job"""
        candidate_vec = np.array(self.skill_vector + self.experience_vector).reshape(1, -1)
        job_vec = np.array(job_vector).reshape(1, -1)
        return float(cosine_similarity(candidate_vec, job_vec)[0][0])

class JobVector(models.Model):
    """Stores pre-computed job vectors for faster matching"""
    job = models.OneToOneField(JobListing, on_delete=models.CASCADE)
    skill_vector = models.JSONField()  # Aggregated required skill vectors
    experience_vector = models.JSONField()  # Vector representing required experience
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Vector for {self.job.title}"

class MatchScore(models.Model):
    """Stores match scores between candidates and jobs"""
    candidate = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(JobListing, on_delete=models.CASCADE)
    score = models.FloatField()  # Similarity score
    skill_match_score = models.FloatField()  # Specific score for skill matching
    experience_match_score = models.FloatField()  # Specific score for experience matching
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('candidate', 'job')
        indexes = [
            models.Index(fields=['candidate', '-score']),  # For finding best jobs for a candidate
            models.Index(fields=['job', '-score']),  # For finding best candidates for a job
        ]

    def __str__(self):
        return f"Match: {self.candidate.username} - {self.job.title} ({self.score})"

class MatchPreference(models.Model):
    """Stores user preferences for job matching"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)
    preferred_locations = models.JSONField(default=list)  # List of preferred locations
    remote_only = models.BooleanField(default=False)
    job_types = models.JSONField(default=list)  # List of preferred job types
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"
