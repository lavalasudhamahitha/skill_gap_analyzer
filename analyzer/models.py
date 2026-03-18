from django.db import models
from django.contrib.auth.models import User

class Branch(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Branches'

class Skill(models.Model):
    name = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.name

class JobRole(models.Model):
    name = models.CharField(max_length=150)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='job_roles')
    
    def __str__(self):
        return f"{self.name} ({self.branch.name})"
        
class RequiredSkill(models.Model):
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.skill.name} for {self.job_role.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    college_name = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return self.full_name

class StudentSkillSelection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skill_selections')
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE)
    match_percentage = models.FloatField(default=0.0)
    missing_skills = models.JSONField(default=list)  # List of skill names that are missing
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job_role.name} - {self.match_percentage}%"
