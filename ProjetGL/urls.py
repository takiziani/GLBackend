"""
URL configuration for ProjetGL project.

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
from django.urls import path , include
import debug_toolbar
from . import views
from App.views import CancelView , SuccessView ,SuccessSubView
from App.views import StripeWebhookView 
# from App import urls as app_urls
from .views import LogoutView
from django.urls import path, re_path
from rest_framework import permissions
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView




urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    path('cancel/', CancelView.as_view(), name='cancel'),
    path('success/', SuccessView.as_view(), name='success'),
    path('sub_success/', SuccessSubView.as_view(), name='sub_success'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('DzSkills/', include('App.urls')  )  ,
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    #path('webhook/stripe/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
]



