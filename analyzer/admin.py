from django.contrib import admin
from .models import Branch, Skill, JobRole, RequiredSkill, UserProfile, StudentSkillSelection

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch')
    list_filter = ('branch',)

@admin.register(RequiredSkill)
class RequiredSkillAdmin(admin.ModelAdmin):
    list_display = ('skill', 'job_role')
    list_filter = ('job_role',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'branch', 'college_name')
    list_filter = ('branch',)

@admin.register(StudentSkillSelection)
class StudentSkillSelectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_role', 'match_percentage', 'created_at')
    list_filter = ('job_role', 'created_at')
