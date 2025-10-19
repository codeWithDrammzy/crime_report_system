from django.urls import path
from .import views

urlpatterns = [
    path('',views.index, name ="") ,
    path("my-login" , views.my_login, name="my-login"),
    path('logout/', views.my_logout, name='logout'),


    # ========= Admin ==========
    path("dashboard" , views.dashboard, name="dashboard"),
    path("department" , views.department_list, name="department"),
    path('officer-list', views.officer_list, name='officer-list'),
    path ('reported-crime', views.reported_crime, name="reported-crime"),
    path('crime-detail/<int:pk>', views.crime_detail, name="crime-detail"),
    path('crime-detail/<int:pk>/', views.crime_detail, name='crime-detail'),
    path('update-report-status/<int:pk>/', views.update_report_status, name='update-report-status'),
    path('search-crime', views.search_crime, name="search-crime"),


    # ========= officer ========
    path('officer-board/', views.officer_board, name='officer-board'),
    path('add-report/', views.add_report, name='add-report'),
    path('report-detail/<int:pk>', views.report_detail, name="report-detail"),
    path('update-status/<int:pk>/', views.update_status, name='update-status'),
    path('mark-notifications-read/', views.mark_notifications_read, name='mark-notifications-read'),
    path('search-report', views.search_report, name="search-report"),

    
]