from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import SkillVector, CandidateVector, JobVector, MatchScore
from Accounts.models import UserProfile, Skill
from DashboardPages.models import JobListing
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class TalentMatchingService:
    def __init__(self):
        # Load pre-trained model for text embeddings
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        
    def _get_text_embedding(self, text):
        """Convert text to embedding vector using BERT"""
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings[0].numpy().tolist()
        except Exception as e:
            logger.error(f"Error generating embedding for text: {text}. Error: {str(e)}")
            return None

    def update_skill_vectors(self):
        """Update or create vectors for all skills"""
        skills = Skill.objects.all()
        for skill in skills:
            vector = self._get_text_embedding(skill.name)
            if vector:
                SkillVector.objects.update_or_create(
                    skill=skill,
                    defaults={'vector': vector}
                )

    def compute_candidate_vector(self, user):
        """Compute and store vector representation for a candidate"""
        try:
            profile = UserProfile.objects.get(user=user)
            
            # Compute skill vector
            skill_vectors = []
            for skill in profile.skills.all():
                skill_vector, _ = SkillVector.objects.get_or_create(
                    skill=skill,
                    defaults={'vector': self._get_text_embedding(skill.name)}
                )
                skill_vectors.append(skill_vector.vector)
            
            if skill_vectors:
                skill_vector = np.mean(skill_vectors, axis=0).tolist()
            else:
                skill_vector = [0] * 768  # Default vector size
            
            # Compute experience vector
            experience_text = f"{profile.years_of_experience} years experience in {', '.join(skill.name for skill in profile.skills.all()[:3])}"
            experience_vector = self._get_text_embedding(experience_text)
            
            # Store vectors
            CandidateVector.objects.update_or_create(
                user=user,
                defaults={
                    'skill_vector': skill_vector,
                    'experience_vector': experience_vector or [0] * 768
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error computing vector for user {user.username}: {str(e)}")
            return False

    def compute_job_vector(self, job):
        """Compute and store vector representation for a job"""
        try:
            # Compute skill vector from required skills
            skill_vectors = []
            for skill in job.skills.all():
                skill_vector, _ = SkillVector.objects.get_or_create(
                    skill=skill,
                    defaults={'vector': self._get_text_embedding(skill.name)}
                )
                skill_vectors.append(skill_vector.vector)
            
            if skill_vectors:
                skill_vector = np.mean(skill_vectors, axis=0).tolist()
            else:
                skill_vector = [0] * 768
            
            # Compute job description vector
            description_vector = self._get_text_embedding(job.description)
            
            # Store vectors
            JobVector.objects.update_or_create(
                job=job,
                defaults={
                    'skill_vector': skill_vector,
                    'experience_vector': description_vector or [0] * 768
                }
            )
            
            return True
        except Exception as e:
            logger.error(f"Error computing vector for job {job.title}: {str(e)}")
            return False

    def compute_match_scores(self, candidate_vector, job_vector):
        """Compute match scores between a candidate and job"""
        try:
            # Compute skill match score
            skill_similarity = cosine_similarity(
                np.array(candidate_vector.skill_vector).reshape(1, -1),
                np.array(job_vector.skill_vector).reshape(1, -1)
            )[0][0]
            
            # Compute experience match score
            experience_similarity = cosine_similarity(
                np.array(candidate_vector.experience_vector).reshape(1, -1),
                np.array(job_vector.experience_vector).reshape(1, -1)
            )[0][0]
            
            # Weighted average of scores
            total_score = 0.7 * skill_similarity + 0.3 * experience_similarity
            
            return {
                'total_score': total_score,
                'skill_match_score': skill_similarity,
                'experience_match_score': experience_similarity
            }
        except Exception as e:
            logger.error(f"Error computing match scores: {str(e)}")
            return None

    def find_matches_for_candidate(self, user, min_score=0.5, limit=20):
        """Find matching jobs for a candidate"""
        try:
            candidate_vector = CandidateVector.objects.get(user=user)
            
            # Get all jobs with vectors
            job_vectors = JobVector.objects.all()
            
            matches = []
            for job_vector in job_vectors:
                scores = self.compute_match_scores(candidate_vector, job_vector)
                if scores and scores['total_score'] >= min_score:
                    matches.append({
                        'job': job_vector.job,
                        'scores': scores
                    })
            
            # Sort by total score and limit results
            matches.sort(key=lambda x: x['scores']['total_score'], reverse=True)
            return matches[:limit]
        
        except Exception as e:
            logger.error(f"Error finding matches for user {user.username}: {str(e)}")
            return []

    def find_matches_for_job(self, job, min_score=0.5, limit=20):
        """Find matching candidates for a job"""
        try:
            job_vector = JobVector.objects.get(job=job)
            
            # Get all candidate vectors
            candidate_vectors = CandidateVector.objects.all()
            
            matches = []
            for candidate_vector in candidate_vectors:
                scores = self.compute_match_scores(candidate_vector, job_vector)
                if scores and scores['total_score'] >= min_score:
                    matches.append({
                        'candidate': candidate_vector.user,
                        'scores': scores
                    })
            
            # Sort by total score and limit results
            matches.sort(key=lambda x: x['scores']['total_score'], reverse=True)
            return matches[:limit]
        
        except Exception as e:
            logger.error(f"Error finding matches for job {job.title}: {str(e)}")
            return []
