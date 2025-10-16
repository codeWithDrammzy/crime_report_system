from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
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

def reported_crime(request):
    reports = CrimeReport.objects.all().order_by('-date_reported')
    context = {'reports': reports}
    return render( request, 'crime_app/adminPage/reported-crime.html',context)

def crime_detail(request, pk):
    report = CrimeReport.objects.get( id=pk )
    context = {'report':report}
    return render( request, 'crime_app/adminPage/crime-detail.html', context)

def crime_detail(request, pk):
    report = get_object_or_404(CrimeReport, id=pk)
    departments = Department.objects.all()
    return render(request, 'crime_app/adminPage/crime-detail.html', {
        'report': report,
        'departments': departments
    })

def update_report_status(request, pk):
    report = get_object_or_404(CrimeReport, id=pk)
    if request.method == 'POST':
        report.status = request.POST.get('status')
        dept_id = request.POST.get('department')
        if dept_id:
            report.department_id = dept_id
        report.save()
        return redirect('crime-detail', pk=report.id)





# ============ Officer page ========
def officer_board(request):
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

    officer_dept = request.user.officer.department
    reports = CrimeReport.objects.filter(department=officer_dept)

    context = {
        'total_reports': reports.count(),
        'resolved_cases': reports.filter(status='Resolved').count(),
        'pending_cases': reports.filter(status='Pending').count(),
        'dismissed_cases': reports.filter(status='Dismissed').count(),
        'recent_reports': reports.order_by('-date_reported')[:8],
        'new_reports': reports.order_by('-date_reported')[:3],
    }

    return render(request, 'crime_app/officerPage/officer-board.html', context)



def add_report(request):
    if request.method == 'POST':
        form = CrimeReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)

            # ✅ Attach evidence files
            report.evidence_image = request.FILES.get('photo_file') or request.FILES.get('evidence_image')
            report.evidence_audio = request.FILES.get('audio_file') or request.FILES.get('evidence_audio')
            report.evidence_video = request.FILES.get('video_file') or request.FILES.get('evidence_video')

            # ✅ Assign reporter (citizen/officer)
            if request.user.is_authenticated:
                report.reporter = request.user

            # ✅ If the officer is reporting, link it to their department
            if hasattr(request.user, 'officer'):
                report.department = request.user.officer.department

            report.save()
            return redirect('officer-board')
    else:
        form = CrimeReportForm()

    # ✅ Officers should only see reports sent *to their department*
    if hasattr(request.user, 'officer'):
        reports = CrimeReport.objects.filter(
            department=request.user.officer.department
        ).order_by('-date_reported')
    else:
        # Regular users or admins see all or just their own (optional)
        reports = CrimeReport.objects.all().order_by('-date_reported')

    return render(request, 'crime_app/officerPage/add-report.html', {
        'form': form,
        'reports': reports
    })


def report_detail(request, pk):
    crime = CrimeReport.objects.get(id = pk)

    context ={'crime':crime}
    return render(request , 'crime_app/officerPage/report-detail.html', context)

def update_status(request, pk):
    report = get_object_or_404(CrimeReport, id=pk)

    # ✅ Only allow updates for officers in the same department
    if hasattr(request.user, 'officer'):
        officer_dept = request.user.officer.department
        if report.department != officer_dept:
            messages.error(request, "You can only update reports in your department.")
            return redirect('report-detail', pk=report.id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
            messages.success(request, f"Report status updated to {new_status}.")
        else:
            messages.error(request, "Please select a valid status.")

    return redirect('report-detail', pk=report.id)
