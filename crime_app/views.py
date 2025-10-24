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
        
        # Find user by email
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            login(request, user)
            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                return redirect('dashboard')
            elif getattr(user, 'role', None) == 'officer':
                return redirect('officer-board')
            else:
                return redirect('user-board')
        else:
            form.add_error(None, 'Invalid email or password')

    return render(request, 'crime_app/homePage/my-login.html', {'form': form})


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(request, 'Account created successfully! Please login to continue.')
            return redirect('my-login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'crime_app/homePage/register.html', {'form': form})


def my_logout(request):
    logout(request)
    return redirect('my-login')

# ===================== ADMIN DASHBOARD =====================

def dashboard(request):
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
    
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
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
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
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
    departments = Department.objects.annotate(officer_count=Count('officers'))
    form = DepartmentForm()

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department created successfully!")
            return redirect('department')

    return render(request, 'crime_app/adminPage/department.html', {
        'departments': departments,
        'form': form,
    })


def reported_crime(request):
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
    reports = CrimeReport.objects.all().order_by('-date_reported' , '-date_updated')
    return render(request, 'crime_app/adminPage/reported-crime.html', {'reports': reports})


def crime_detail(request, pk):
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
    report = get_object_or_404(CrimeReport, id=pk)
    departments = Department.objects.all()
    return render(request, 'crime_app/adminPage/crime-detail.html', {
        'report': report,
        'departments': departments
    })


def update_report_status(request, pk):
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
    report = get_object_or_404(CrimeReport, id=pk)
    if request.method == 'POST':
        old_status = report.status  # Store old status for comparison
        old_dept = report.department
        new_status = request.POST.get('status')
        dept_id = request.POST.get('department')

        if dept_id:
            report.department_id = dept_id

        report.status = new_status
        report.save()

        # ✅ CREATE CITIZEN NOTIFICATION FOR STATUS CHANGE
        if old_status != new_status:
            CitizenNotification.objects.create(
                user=report.reporter,
                notification_type='status_update',
                title='Report Status Updated',
                message=f'Your report "{report.title}" status has been changed from {old_status} to {new_status} by Administrator.',
                related_report=report
            )

        # ✅ CREATE CITIZEN NOTIFICATION FOR DEPARTMENT REASSIGNMENT
        if dept_id and str(old_dept.id) != str(dept_id):
            new_department = Department.objects.get(id=dept_id)
            CitizenNotification.objects.create(
                user=report.reporter,
                notification_type='assignment',
                title='Report Reassigned',
                message=f'Your report "{report.title}" has been reassigned from {old_dept.name} to {new_department.name}.',
                related_report=report
            )

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
    # Check if user is admin
    if not request.user.is_authenticated or (not request.user.is_superuser and getattr(request.user, 'role', None) != 'admin'):
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('my-login')
        
    query = request.GET.get('q', '')
    results = []

    if query:
        results = CrimeReport.objects.filter(
            Q(pk__icontains=query) |
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
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

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

            messages.success(request, "Crime report submitted successfully!")
            return redirect('officer-board')
    else:
        form = CrimeReportForm()

    reports = CrimeReport.objects.filter(department=request.user.officer.department).order_by('-date_reported')
    return render(request, 'crime_app/officerPage/add-report.html', {'form': form, 'reports': reports})


def report_detail(request, pk):
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

    crime = get_object_or_404(CrimeReport, id=pk)
    
    # Check if officer has access to this report
    if crime.department != request.user.officer.department:
        messages.error(request, "You can only access reports from your department.")
        return redirect('officer-board')
        
    return render(request, 'crime_app/officerPage/report-detail.html', {'crime': crime})


def update_status(request, pk):
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

    report = get_object_or_404(CrimeReport, id=pk)

    if hasattr(request.user, 'officer'):
        officer = request.user.officer
        if report.department != officer.department:
            messages.error(request, "You can only update reports within your department.")
            return redirect('report-detail', pk=report.id)

    if request.method == 'POST':
        old_status = report.status  # Store old status for comparison
        new_status = request.POST.get('status')
        if new_status:
            report.status = new_status
            report.save()
            
            # ✅ CREATE CITIZEN NOTIFICATION FOR STATUS CHANGE
            if old_status != new_status:
                CitizenNotification.objects.create(
                    user=report.reporter,
                    notification_type='status_update',
                    title='Report Status Updated',
                    message=f'Your report "{report.title}" status has been updated from {old_status} to {new_status} by Officer {request.user.get_full_name()} from {report.department.name}.',
                    related_report=report
                )
            
            # Notify other officers in department
            officers = Officer.objects.filter(department=report.department)
            for o in officers:
                if o != request.user.officer:  # Don't notify the officer who made the change
                    Notification.objects.create(
                        officer=o,
                        message=f"⚙️ The status of case '{report.title}' has been updated to {new_status} by {request.user.get_full_name()}."
                    )
            
            messages.success(request, f"Report status updated to {new_status}.")
        else:
            messages.error(request, "Please select a valid status.")

    return redirect('report-detail', pk=report.id)


# ===================== SEARCH CRIME (OFFICER) =====================
def search_report(request):
    if not hasattr(request.user, 'officer'):
        messages.error(request, "Only officers can access this page.")
        return redirect('my-login')

    officer = request.user.officer
    officer_dept = officer.department

    query = request.GET.get('q', '')
    results = []

    if query:
        results = CrimeReport.objects.filter(
            Q(department=officer_dept) & (
                Q(report_id__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(incident_type__icontains=query)
            )
        )
    else:
        # Optional: show all reports for this officer if no query
        results = CrimeReport.objects.filter(department=officer_dept)

    context = {
        'results': results,
        'query': query
    }
    return render(request, 'crime_app/officerPage/search-report.html', context)


# ===================== CITIZEN DASHBOARD =====================

def user_board(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to access your dashboard.")
        return redirect('my-login')
    
    # Check if user is citizen
    if hasattr(request.user, 'officer') or (request.user.is_superuser or getattr(request.user, 'role', None) == 'admin'):
        messages.error(request, "This page is for citizens only.")
        return redirect('dashboard' if request.user.is_superuser or getattr(request.user, 'role', None) == 'admin' else 'officer-board')
    
    # Get all user reports first
    user_reports = CrimeReport.objects.filter(reporter=request.user).order_by('-date_reported')
    
    # Calculate counts from the original queryset (before slicing)
    total_reports = user_reports.count()
    resolved_reports = user_reports.filter(status='Resolved').count()
    pending_reports = user_reports.filter(status='Pending').count()
    
    # Get recent reports (slice after all filtering is done)
    recent_reports = user_reports[:4]
    
    # ✅ GET UNREAD NOTIFICATION COUNT
    unread_count = CitizenNotification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'recent_reports': recent_reports,
        'unread_count': unread_count,  # Add this to context
    }
    return render(request, 'crime_app/citizenPage/user-board.html', context)

def user_report(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to report a crime.")
        return redirect('my-login')
    
    # Check if user is citizen
    if hasattr(request.user, 'officer') or (request.user.is_superuser or getattr(request.user, 'role', None) == 'admin'):
        messages.error(request, "Officers and admins cannot submit citizen reports.")
        return redirect('dashboard' if request.user.is_superuser or getattr(request.user, 'role', None) == 'admin' else 'officer-board')
    
    if request.method == 'POST':
        print("=== FORM SUBMISSION DEBUG ===")
        print("POST data keys:", list(request.POST.keys()))
        print("FILES data keys:", list(request.FILES.keys()))
        
        form = CrimeReportForm(request.POST, request.FILES)
        print("Form is valid:", form.is_valid())
        
        if not form.is_valid():
            print("Form errors:", form.errors.as_json())
            for field, errors in form.errors.items():
                print(f"Field '{field}': {errors}")
        
        if form.is_valid():
            print("Form is valid, saving report...")
            report = form.save(commit=False)
            report.reporter = request.user
            
            # Handle GPS coordinates (no rounding needed with FloatField)
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')
            print(f"GPS Coordinates - Lat: {latitude}, Lng: {longitude}")
            
            # FloatField will handle the conversion automatically
            if latitude and longitude:
                report.latitude = latitude
                report.longitude = longitude
                print("GPS coordinates saved")
            
            # Handle media files from live capture
            if 'photo_file' in request.FILES:
                report.evidence_image = request.FILES['photo_file']
                print("Using photo_file from live capture")
            elif not report.evidence_image:
                print("No photo evidence provided")
                
            if 'video_file' in request.FILES:
                report.evidence_video = request.FILES['video_file']
                print("Using video_file from live capture")
            elif not report.evidence_video:
                print("No video evidence provided")
                
            if 'audio_file' in request.FILES:
                report.evidence_audio = request.FILES['audio_file']
                print("Using audio_file from live capture")
            elif not report.evidence_audio:
                print("No audio evidence provided")
            
            try:
                report.save()
                print("✅ Report saved successfully! ID:", report.id)
                
                # ✅ FIXED: Notify officers in the selected department (remove 'report' parameter)
                if report.department:
                    officers = Officer.objects.filter(department=report.department)
                    notification_count = 0
                    for officer in officers:
                        Notification.objects.create(
                            officer=officer,
                            message=f"🚨 New crime reported in your department: {report.title} (Report ID: {report.id})"
                            # Remove the 'report' parameter as Notification model doesn't have this field
                        )
                        notification_count += 1
                    
                    messages.success(request, f"Crime report submitted successfully to {report.department.name}! {notification_count} officers notified.")
                else:
                    messages.success(request, "Crime report submitted successfully!")

                return redirect('user-board')
                
            except Exception as e:
                print("❌ Error saving report:", str(e))
                messages.error(request, f"Error saving report: {str(e)}")
        else:
            print("❌ Form has validation errors")
            # Show specific field errors to user
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CrimeReportForm()
        print("GET request - showing empty form")

    context = {
        'form': form,
    }
    return render(request, 'crime_app/citizenPage/user-report.html', context)

def report_history(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view your report history.")
        return redirect('my-login')
    
    # Check if user is citizen
    if hasattr(request.user, 'officer') or (request.user.is_superuser or getattr(request.user, 'role', None) == 'admin'):
        messages.error(request, "This page is for citizens only.")
        return redirect('dashboard' if request.user.is_superuser or getattr(request.user, 'role', None) == 'admin' else 'officer-board')
    
    user_reports = CrimeReport.objects.filter(reporter=request.user).order_by('-date_reported')
    
    # Calculate stats for the template
    total_reports = user_reports.count()
    pending_reports = user_reports.filter(status='Pending').count()
    resolved_reports = user_reports.filter(status='Resolved').count()
    dismissed_reports = user_reports.filter(status='Dismissed').count()
    
    context = {
        'reports': user_reports,
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'resolved_reports': resolved_reports,
        'dismissed_reports': dismissed_reports,
    }
    return render(request, 'crime_app/citizenPage/report-history.html', context)


def c_report_detail(request, pk):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view report details.")
        return redirect('my-login')
    
    try:
        report = CrimeReport.objects.get(id=pk)
        
        # Check if the user owns this report or is an officer/admin
        if report.reporter != request.user and not (hasattr(request.user, 'officer') or request.user.is_superuser):
            messages.error(request, "You don't have permission to view this report.")
            return redirect('user-board')
            
    except CrimeReport.DoesNotExist:
        messages.error(request, "Report not found.")
        return redirect('user-board')
    
    context = {
        'report': report,
    }
    return render(request, 'crime_app/citizenPage/c-report-detail.html', context)


# views.py - Add these views
def citizen_notifications(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login to view notifications.")
        return redirect('my-login')
    
    notifications = CitizenNotification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'crime_app/citizenPage/notifications.html', context)

@csrf_exempt
def mark_notification_read(request, notification_id):
    if request.method == "POST" and request.user.is_authenticated:
        try:
            notification = CitizenNotification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success'})
        except CitizenNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notification not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@csrf_exempt
def mark_all_notifications_read(request):
    if request.method == "POST" and request.user.is_authenticated:
        CitizenNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})




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