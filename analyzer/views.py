from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

from .models import Branch, Skill, JobRole, RequiredSkill, UserProfile, StudentSkillSelection

def home(request):
    return render(request, 'analyzer/home.html')

def about(request):
    return render(request, 'analyzer/about.html')

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        branch_id = request.POST.get('branch')
        college_name = request.POST.get('college_name')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('register')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect('register')

        # Create user
        user = User.objects.create_user(username=email, email=email, password=password)
        
        # Create user profile
        branch = Branch.objects.get(id=branch_id) if branch_id else None
        UserProfile.objects.create(
            user=user, 
            full_name=full_name, 
            branch=branch, 
            college_name=college_name
        )
        
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect('home')

    branches = Branch.objects.all()
    return render(request, 'analyzer/register.html', {'branches': branches})

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('analyzer_tool')
        else:
            messages.error(request, "Invalid email or password")
            
    return render(request, 'analyzer/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def analyzer_tool(request):
    branches = Branch.objects.all()
    # If the user has a branch in profile, we can pre-select it
    user_profile = getattr(request.user, 'profile', None)
    return render(request, 'analyzer/tool.html', {
        'branches': branches,
        'user_profile': user_profile
    })

@login_required
def get_branch_data(request, branch_id):
    """API endpoint to get skills and job roles dynamically based on branch"""
    branch = get_object_or_404(Branch, id=branch_id)
    
    # Get all job roles for this branch
    job_roles = list(JobRole.objects.filter(branch=branch).values('id', 'name'))
    
    # Get all distinct skills required by any job role in this branch
    # This helps show only relevant skills to the student
    required_skills = RequiredSkill.objects.filter(job_role__branch=branch).select_related('skill')
    
    # If database is empty, we'll return all skills as fallback, but ideally 
    # we filter by relationship.
    if required_skills.exists():
        skills_set = set()
        for rs in required_skills:
            skills_set.add((rs.skill.id, rs.skill.name))
        skillsList = [{'id': s[0], 'name': s[1]} for s in skills_set]
    else:
        # Fallback if no required skills are mapped yet
        skillsList = list(Skill.objects.all().values('id', 'name'))
        
    # Sort skills alphabetically
    skillsList.sort(key=lambda x: x['name'])
    
    return JsonResponse({
        'job_roles': job_roles,
        'skills': skillsList
    })

@login_required
def submit_analysis(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_role_id = data.get('job_role_id')
            student_skill_ids = data.get('student_skills', []) # List of selected skill IDs
            
            job_role = get_object_or_404(JobRole, id=job_role_id)
            
            # Get required skills for this job role
            required_skills_qs = RequiredSkill.objects.filter(job_role=job_role).select_related('skill')
            required_skill_ids = set([rs.skill.id for rs in required_skills_qs])
            
            student_skill_ids_set = set(int(id) for id in student_skill_ids)
            
            # Calculate missing skills
            missing_skill_ids = required_skill_ids - student_skill_ids_set
            
            match_percentage = 100.0
            if required_skill_ids:
                match_percentage = ((len(required_skill_ids) - len(missing_skill_ids)) / len(required_skill_ids)) * 100
                
            match_percentage = round(match_percentage, 1)
            
            # Get names of missing skills for the result
            missing_skills = list(Skill.objects.filter(id__in=missing_skill_ids).values_list('name', flat=True))
            
            # Save the result
            selection = StudentSkillSelection.objects.create(
                user=request.user,
                job_role=job_role,
                match_percentage=match_percentage,
                missing_skills=missing_skills
            )
            
            return JsonResponse({
                'success': True,
                'redirect_url': f'/result/{selection.id}/'
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

LEARNING_RESOURCES = {
    'Python': 'https://www.w3schools.com/python/',
    'Java': 'https://www.geeksforgeeks.org/java/',
    'HTML': 'https://www.w3schools.com/html/',
    'CSS': 'https://www.w3schools.com/css/',
    'JavaScript': 'https://javascript.info/',
    'React': 'https://react.dev/learn',
    'Node.js': 'https://nodejs.dev/learn',
    'Django': 'https://docs.djangoproject.com/en/stable/intro/',
    'SQL': 'https://www.w3schools.com/sql/',
    'MongoDB': 'https://www.mongodb.com/docs/manual/tutorial/getting-started/',
    'Machine Learning': 'https://www.geeksforgeeks.org/machine-learning/',
    'Data Structures': 'https://www.geeksforgeeks.org/data-structures/',
    'Algorithms': 'https://www.geeksforgeeks.org/fundamentals-of-algorithms/',
    'C': 'https://www.w3schools.com/c/',
    'C++': 'https://www.w3schools.com/cpp/',
    'Data Analysis': 'https://www.datacamp.com/tutorial/category/data-analysis',
    'AWS': 'https://aws.amazon.com/getting-started/',
    'Docker': 'https://docs.docker.com/get-started/',
    'Git': 'https://git-scm.com/book/en/v2',
    'AutoCAD': 'https://www.autodesk.com/campaigns/autocad-tutorials',
    'Linux': 'https://linuxjourney.com/',
}

@login_required
def analysis_result(request, selection_id):
    selection = get_object_or_404(StudentSkillSelection, id=selection_id, user=request.user)
    
    missing_skills_data = []
    for skill in selection.missing_skills:
        link = LEARNING_RESOURCES.get(skill, f"https://www.google.com/search?q={skill}+study+notes+tutorial")
        missing_skills_data.append({
            'name': skill,
            'link': link
        })
    
    return render(request, 'analyzer/result.html', {
        'selection': selection,
        'missing_skills': missing_skills_data
    })
