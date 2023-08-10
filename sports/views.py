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
from django.contrib.messages.views import SuccessMessageMixin
from .forms import TeamForm, PlayerForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .models import Team, Player


class NamedSuccessMessageMixin(SuccessMessageMixin):
    """Fill %(name)s from the saved or deleted object rather than the form data."""

    def get_success_message(self, cleaned_data):
        return self.success_message % {"name": self.object}


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        context = {
            "team_count": Team.objects.count(),
            "player_count": Player.objects.count(),
            "unassigned_count": Player.objects.filter(teams__isnull=True).count(),
        }
        return render(request, "index.html", context)


class TeamListView(LoginRequiredMixin, ListView):
    model = Team
    template_name = "team_list.html"
    context_object_name = "teams"
    paginate_by = 25
    queryset = Team.objects.order_by("city", "mascot", "pk")


class TeamCreateView(LoginRequiredMixin, NamedSuccessMessageMixin, CreateView):
    model = Team
    form_class = TeamForm
    template_name = "team_form.html"
    success_url = reverse_lazy("team_list")
    success_message = "Added %(name)s."


class TeamUpdateView(LoginRequiredMixin, NamedSuccessMessageMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "team_form.html"
    success_url = reverse_lazy("team_list")
    success_message = "Saved %(name)s."


class TeamDeleteView(LoginRequiredMixin, NamedSuccessMessageMixin, DeleteView):
    model = Team
    template_name = "team_confirm_delete.html"
    success_url = reverse_lazy("team_list")
    success_message = "Deleted %(name)s."


class TeamDetailView(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "team_detail.html"
    context_object_name = "team"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["roster"] = self.object.player_set.order_by("last_name", "first_name")
        return context


class PlayerListView(LoginRequiredMixin, ListView):
    model = Player
    template_name = "player_list.html"
    context_object_name = "players"
    paginate_by = 25
    queryset = Player.objects.prefetch_related("teams").order_by("last_name", "first_name", "pk")


class PlayerCreateView(LoginRequiredMixin, NamedSuccessMessageMixin, CreateView):
    model = Player
    form_class = PlayerForm
    template_name = "player_form.html"
    success_url = reverse_lazy("player_list")
    success_message = "Added %(name)s."


class PlayerUpdateView(LoginRequiredMixin, NamedSuccessMessageMixin, UpdateView):
    model = Player
    form_class = PlayerForm
    template_name = "player_form.html"
    success_url = reverse_lazy("player_list")
    success_message = "Saved %(name)s."


class PlayerDeleteView(LoginRequiredMixin, NamedSuccessMessageMixin, DeleteView):
    model = Player
    template_name = "player_confirm_delete.html"
    success_url = reverse_lazy("player_list")
    success_message = "Deleted %(name)s."


class PlayerDetailView(LoginRequiredMixin, DetailView):
    model = Player
    template_name = "player_detail.html"
    context_object_name = "player"


class SignUpView(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "signup.html"
    success_message = "Account created. Log in to continue."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)


class SignInView(LoginView):
    template_name = "login.html"
    redirect_authenticated_user = True


class LogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse_lazy("login"))


def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


def custom_500_view(request):
    return render(request, "500.html", status=500)
