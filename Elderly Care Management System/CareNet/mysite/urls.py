"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from CareNet.views import (login, logout, create_user_view, home, create_patient_profile, search_patient_profile, update_patient_profile, delete_patient_profile,
                           medical_dashboard, patient_medical_dashboard_details, download_medical_file, maintenance_mode, roster_view,
                           add_roster_view, delete_roster_view, maintenance_status, care_planner_search, patient_care_planner_details)
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('create_user/', create_user_view, name='create_user'),
    path('', home, name='home'),
    path('maintenance/', maintenance_mode, name='maintenance_mode'),
    path('maintenance-status/', maintenance_status, name='maintenance_status'),
    path('create_patient/', create_patient_profile, name='create_patient_profile'),
    path('search_patient/', search_patient_profile, name='search_patient_profile'),
    path('update_patient/', update_patient_profile, name='update_patient_profile'),
    path('delete_patient/', delete_patient_profile, name='delete_patient_profile'),
    path('medical-dashboard/', medical_dashboard, name='medical_dashboard'),
    path('medical-dashboard/details/<int:patient_id>/', patient_medical_dashboard_details, name='patient_medical_dashboard_details'),
    path('medical-dashboard/download/<int:patient_id>/<int:file_index>/', download_medical_file, name='download_medical_file'),
    path('roster/', roster_view, name='roster'),
    path('roster/add', add_roster_view, name='add_roster'),#
    path('roster/delete/<int:roster_id>/', delete_roster_view, name='delete_roster'),
    path('care_planner/', care_planner_search, name='care_planner'),
    path('care_planner/<int:patient_id>/', patient_care_planner_details, name='patient_care_planner_details')
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)