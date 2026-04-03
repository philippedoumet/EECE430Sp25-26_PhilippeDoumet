from django.urls import path
from . import views

urlpatterns = [
    path('', views.PlayerListView.as_view(), name='player_list'),
    path('new/', views.PlayerCreateView.as_view(), name='player_create'),
    path('<int:pk>/edit/', views.PlayerUpdateView.as_view(), name='player_update'),
    path('<int:pk>/delete/', views.PlayerDeleteView.as_view(), name='player_delete'),
]