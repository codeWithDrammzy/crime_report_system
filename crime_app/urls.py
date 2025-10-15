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

    # ========= officer ========
    path('officer-board/', views.officer_board, name='officer-board'),
    path('add-report/', views.add_report, name='add-report'),
    path('report-detail/<int:pk>', views.report_detail, name="report-detail"),
    
]