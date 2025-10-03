from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
  
    
    path('terms/', views.terms_view, name='terms'),
    path('resend-verification/', views.resend_email_verification, name='account_resend_email'),
    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/', views.profile_dashboard, name='profile_edit'),
  
]
