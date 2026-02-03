from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_http_methods


def login_view(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')


@login_required(login_url='login')
def dashboard(request):
    """Dashboard page"""
    return render(request, 'dashboard.html')


@login_required(login_url='login')
def projects(request):
    """Projects list page"""
    return render(request, 'projects.html')


@login_required(login_url='login')
def project_detail(request, project_id):
    """Project detail page"""
    return render(request, 'project-detail.html', {'project_id': project_id})


@login_required(login_url='login')
def review(request):
    """Review projects page"""
    if request.user.role not in ['reviewer', 'qa']:
        return render(request, '403.html', status=403)
    return render(request, 'review.html')


@login_required(login_url='login')
def admin(request):
    """Admin page"""
    if request.user.role != 'qa':
        return render(request, '403.html', status=403)
    return render(request, 'admin_panel.html')


@login_required(login_url='login')
def re_analysis(request):
    """Re-analysis request page"""
    project_id = request.GET.get('project')
    step = request.GET.get('step')

    if not project_id or not step:
        return render(request, 'error.html', {'error': 'Invalid re-analysis request parameters'})

    # Check if user has access to this project
    try:
        from apps.projects.models import Project
        project = Project.objects.get(id=project_id, created_by=request.user)
        return render(request, 're-analysis.html')
    except Project.DoesNotExist:
        return render(request, '403.html', status=403)


@login_required(login_url='login')
def settings(request):
    """User settings page"""
    return render(request, 'settings.html')
