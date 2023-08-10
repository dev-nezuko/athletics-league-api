from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.views import View
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import TeamForm, PlayerForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .models import Team, Player


class Test(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "index.html")


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "team_list.html"
    context_object_name = "teams"


class TeamCreateView(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "team_form.html"
    success_url = reverse_lazy("team_list")


class TeamUpdateView(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "team_form.html"
    success_url = reverse_lazy("team_list")


class TeamDeleteView(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = "team_confirm_delete.html"
    success_url = reverse_lazy("team_list")


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "team_detail.html"
    context_object_name = "team"


class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template_name = "player_list.html"
    context_object_name = "players"


class PlayerCreateView(LoginRequiredMixin, CreateView):
    model = Player
    form_class = PlayerForm
    template_name = "player_form.html"
    success_url = reverse_lazy("player_list")


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = "player_form.html"
    success_url = reverse_lazy("player_list")


class PlayerDeleteView(LoginRequiredMixin, DeleteView):
    model = Player
    template_name = "player_confirm_delete.html"
    success_url = reverse_lazy("player_list")


class PlayerDetailView(LoginRequiredMixin, DetailView):
    model = Player
    template_name = "player_detail.html"
    context_object_name = "player"


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"


class LoginView(LoginView):
    form_class = AuthenticationForm
    success_url = reverse_lazy("team_list")
    template_name = "login.html"


class LogoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse_lazy("login"))


def custom_404_view(request, exception):
    return render(request, "404.html")


def custom_500_view(request):
    return render(request, "500.html")
