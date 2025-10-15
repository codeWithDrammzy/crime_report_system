from django.shortcuts import render, HttpResponse, redirect
from .forms import *
from django.contrib.auth import authenticate, login, logout
from .models import *
from django.contrib import messages  
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count


def index(request):
    return render( request, 'crime_app/homePage/index.html')


def my_login(request):
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        # Make sure 'username=email' is used (not 'user=email')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                return redirect('dashboard')
            elif getattr(user, 'role', None) == 'officer':
                return redirect("officer-board")
            else:
                return redirect("user_board")
        else:
            # Add error if login fails
            form.add_error(None, 'Invalid email or password')

    context = {'form': form}
    return render(request, 'crime_app/homePage/my-login.html', context)

def my_logout(request):
    logout(request)
    return redirect('my-login') 

# ============= Admin page==========
def dashboard(request):
    total_reports = CrimeReport.objects.count()
    resolved_cases = CrimeReport.objects.filter(status='Resolved').count()
    pending_reports = CrimeReport.objects.filter(status='Pending').count()
    total_departments = Department.objects.count()

    # Get 5 most recent reports (if any)
    recent_reports = CrimeReport.objects.select_related('reporter').order_by('-date_reported')[:5]

    context = {
        'total_reports': total_reports,
        'resolved_cases': resolved_cases,
        'pending_reports': pending_reports,
        'total_departments': total_departments,
        'recent_reports': recent_reports,
    }
    return render(request, 'crime_app/adminPage/dashboard.html', context)

def officer_list(request):
    if request.method == 'POST':
        form = OfficerForm(request.POST, request.FILES)
        if form.is_valid():
            officer = form.save(commit=False)
            officer.save()
            messages.success(request, f"Officer {officer.user.get_full_name()} added successfully!")
            return redirect('officer-list')
    else:
        form = OfficerForm()

    officers = Officer.objects.all()
    return render(request, 'crime_app/adminPage/officer-list.html', {'form': form, 'officers': officers})

def department_list(request):
    departments = Department.objects.annotate(officer_count=Count('officers'))  
    form = DepartmentForm()

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('department')

    context = {
        'departments': departments,
        'form': form,
    }
    return render(request, 'crime_app/adminPage/department.html', context)

# ============ Officer page ========
def officer_board(request):
    return render(request , 'crime_app/officerPage/officer-board.html')



def add_report(request):
    if request.method == 'POST':
        form = CrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)

            # ✅ Attach evidence files (from form or JS)
            report.evidence_image = request.FILES.get('photo_file') or request.FILES.get('evidence_image')
            report.evidence_audio = request.FILES.get('audio_file') or request.FILES.get('evidence_audio')
            report.evidence_video = request.FILES.get('video_file') or request.FILES.get('evidence_video')

            # ✅ Assign department automatically if officer
            if hasattr(request.user, 'officer'):
                report.department = request.user.officer.department

            # ✅ Attach reporter (citizen/officer)
            if request.user.is_authenticated:
                report.reporter = request.user

            report.save()
            return redirect('officer-board')
    else:
        form = CrimeReportForm()

    reports = CrimeReport.objects.all().order_by('-date_reported')
    return render(request, 'crime_app/officerPage/add-report.html', {
        'form': form,
        'reports': reports
    })


def report_detail(request, pk):
    crime = CrimeReport.objects.get(id = pk)

    context ={'crime':crime}
    return render(request , 'crime_app/officerPage/report-detail.html', context)