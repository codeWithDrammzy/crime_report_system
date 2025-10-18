from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import *
from .forms import *

User = get_user_model()

# ===================== HOME PAGE =====================
def index(request):
    return render(request, 'crime_app/homePage/index.html')


# ===================== AUTHENTICATION =====================
def my_login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                return redirect('dashboard')
            elif getattr(user, 'role', None) == 'officer':
                return redirect('officer-board')
            else:
                return redirect('user_board')
        else:
            form.add_error(None, 'Invalid email or password')

    return render(request, 'crime_app/homePage/my-login.html', {'form': form})


def my_logout(request):
    logout(request)
    return redirect('my-login')


# ===================== ADMIN DASHBOARD =====================
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
            officer = form.save()
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

    return render(request, 'crime_app/adminPage/department.html', {
        'departments': departments,
        'form': form,
    })


def reported_crime(request):
    reports = CrimeReport.objects.all().order_by('status')
    return render(request, 'crime_app/adminPage/reported-crime.html', {'reports': reports})


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
        old_dept = report.department
        new_status = request.POST.get('status')
        dept_id = request.POST.get('department')

        if dept_id:
            report.department_id = dept_id

        report.status = new_status
        report.save()

        # Notify new department officers if reassigned
        if dept_id and str(old_dept.id) != str(dept_id):
            officers = Officer.objects.filter(department_id=dept_id)
            for officer in officers:
                Notification.objects.create(
                    officer=officer,
                    message=f"📢 New case '{report.title}' has been assigned to your department."
                )

        messages.success(request, "Report updated successfully!")
        return redirect('crime-detail', pk=report.id)


# ===================== SEARCH CRIME =====================
def search_crime(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        results = CrimeReport.objects.filter(
            Q(report_id__icontains=query) |
            Q(location__icontains=query) |
            Q(status__icontains=query) |
            Q(incident_type__icontains=query)
        )

    context = {
        'results': results,
        'query': query
    }
    return render(request, 'crime_app/adminPage/search-crime.html', context)


# ===================== OFFICER DASHBOARD =====================
def officer_board(request):
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

    officer = request.user.officer
    officer_dept = officer.department
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
            report.evidence_image = request.FILES.get('photo_file') or request.FILES.get('evidence_image')
            report.evidence_audio = request.FILES.get('audio_file') or request.FILES.get('evidence_audio')
            report.evidence_video = request.FILES.get('video_file') or request.FILES.get('evidence_video')
            if request.user.is_authenticated:
                report.reporter = request.user
            if hasattr(request.user, 'officer'):
                report.department = request.user.officer.department
            report.save()

            # Notify officers
            if report.department:
                officers = Officer.objects.filter(department=report.department)
                for officer in officers:
                    Notification.objects.create(
                        officer=officer,
                        message=f"🚨 New crime reported in your department: {report.title}"
                    )

            return redirect('officer-board')
    else:
        form = CrimeReportForm()

    reports = CrimeReport.objects.filter(department=request.user.officer.department).order_by('-date_reported')
    return render(request, 'crime_app/officerPage/add-report.html', {'form': form, 'reports': reports})


def report_detail(request, pk):
    crime = get_object_or_404(CrimeReport, id=pk)
    return render(request, 'crime_app/officerPage/report-detail.html', {'crime': crime})


def update_status(request, pk):
    report = get_object_or_404(CrimeReport, id=pk)

    if hasattr(request.user, 'officer'):
        officer = request.user.officer
        if report.department != officer.department:
            messages.error(request, "You can only update reports within your department.")
            return redirect('report-detail', pk=report.id)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
            officers = Officer.objects.filter(department=report.department)
            for o in officers:
                Notification.objects.create(
                    officer=o,
                    message=f"⚙️ The status of case '{report.title}' has been updated to {new_status}."
                )
            messages.success(request, f"Report status updated to {new_status}.")
        else:
            messages.error(request, "Please select a valid status.")

    return redirect('report-detail', pk=report.id)


# ===================== NOTIFICATIONS =====================
@csrf_exempt
def mark_notifications_read(request):
    if request.method == "POST":
        if hasattr(request.user, "officer"):
            Notification.objects.filter(officer=request.user.officer, is_read=False).update(is_read=True)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "error", "message": "User is not an officer"}, status=403)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)
