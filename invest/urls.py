from django.urls import path
from . import views

urlpatterns = [
    path('', views.webapp_home, name='webapp_home'),
    path('api/captcha/', views.get_captcha, name='get_captcha'),
    path('api/verify/', views.verify_captcha, name='verify_captcha'),
]
