from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.SetupView.as_view(), name='setup'),
    path('setup/done/', views.SetupDoneView.as_view(), name='setup_done'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
