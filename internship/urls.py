"""
URL configuration for internship project.

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
from django.urls import path, include
from rest_framework import routers
from ehr.views import create_record, get_record, deleteRecord, create_user, delete_user, get_user, updateRecord, create_doctor, get_doctor, create_appointment, get_appointment, reschedule_appointment, cancel_appointment
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView


urlpatterns = [
    
   # Include your app's URLs
    # Include ViewSets

    # Manually add APIView routes
    path('admin/', admin.site.urls),
    path('api/create_user/', create_user.as_view(), name='create_user'),
    path('api/create_record/', create_record.as_view(), name='create_record'),
    path('api/delete/<int:pk>/', deleteRecord.as_view(), name='delete_record'),
    path('api/get_record/<int:pk>/', get_record.as_view(), name='get_record'),
    path('api/delete_user/<int:pk>/', delete_user.as_view(), name='delete_user'),
    path('api/get_user/<int:pk>/', get_user.as_view(), name='get_user'),
    path('api/update_record/<int:pk>/', updateRecord.as_view(), name='update_record'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/create_doctor/', create_doctor.as_view(), name='create_doctor'),
    path('api/get_doctor/', get_doctor.as_view(), name='get_doctor'),
    path('api/create_appointment/', create_appointment.as_view(), name='create_appointment'),
    path('api/get_appointment/<int:pk>/', get_appointment.as_view(), name='get_appointment'),
    path('api/reschedule_appointment/<int:pk>/', reschedule_appointment.as_view(), name='reschedule_appointment'),
    path('api/cancel_appointment/<int:pk>/', cancel_appointment.as_view(), name='cancel_appointment'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)