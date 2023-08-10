from django.urls import path
from .views import (
    TeamListView,
    TeamCreateView,
    TeamDetailView,
    TeamUpdateView,
    TeamDeleteView,
    PlayerListView,
    PlayerCreateView,
    PlayerDetailView,
    PlayerUpdateView,
    PlayerDeleteView,
    LoginView,
    SignUpView,
    LogoutView,
    Test,
)

urlpatterns = [
    path('', Test.as_view(), name='home'),
    path('team/', TeamListView.as_view(), name='team_list'),
    path('team/new/', TeamCreateView.as_view(), name='team_create'),
    path('team/<int:pk>/', TeamDetailView.as_view(), name='team_detail'),
    path('team/<int:pk>/update/', TeamUpdateView.as_view(), name='team_update'),
    path('team/<int:pk>/delete/', TeamDeleteView.as_view(), name='team_delete'),

    path('player/', PlayerListView.as_view(), name='player_list'),
    path('player/new/', PlayerCreateView.as_view(), name='player_create'),
    path('player/<int:pk>/', PlayerDetailView.as_view(), name='player_detail'),
    path('player/<int:pk>/update/', PlayerUpdateView.as_view(), name='player_update'),
    path('player/<int:pk>/delete/', PlayerDeleteView.as_view(), name='player_delete'),

    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', SignUpView.as_view(), name='signup'),

]

