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
from CareNet.views import home, create_patient_profile, search_patient_profile, update_patient_profile, delete_patient_profile, maintenance_mode
from django.views.generic import RedirectView

urlpatterns = [
    path('', home, name='home'),
    path('maintenance/', maintenance_mode, name='maintenance_mode'),
    path('create_patient/', create_patient_profile, name='create_patient_profile'),
    path('search_patient/', search_patient_profile, name='search_patient_profile'),
    path('update_patient/', update_patient_profile, name='update_patient_profile'),
    path('delete_patient/', delete_patient_profile, name='delete_patient_profile'),
]
