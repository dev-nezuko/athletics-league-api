from django.contrib.auth.models import AnonymousUser, User
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import reverse

from .models import Player, Team
from .views import PlayerListView, custom_500_view


class RosterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("synthetic-reviewer", password="local-test-password")
        self.client.force_login(self.user)
        self.team = Team.objects.create(city="Northwind", mascot="Owls")
        self.player = Player.objects.create(first_name="Casey", last_name="Example")
        self.player.teams.add(self.team)

    def test_anonymous_lists_require_login(self):
        self.client.logout()
        self.assertRedirects(self.client.get("/team/"), "/login/?next=/team/")

    def test_player_details_render_memberships(self):
        response = self.client.get(reverse("player_detail", args=[self.player.pk]))
        self.assertContains(response, "Northwind")
        self.assertContains(response, "Casey")

    def test_team_details_render_reverse_membership(self):
        response = self.client.get(reverse("team_detail", args=[self.team.pk]))
        self.assertContains(response, "Casey")

    def test_get_cannot_log_out(self):
        self.assertEqual(self.client.get("/logout/").status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_requires_csrf_with_real_checks(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        self.assertEqual(client.post("/logout/").status_code, 403)
        client.get("/team/")
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post("/logout/", {"csrfmiddlewaretoken": token}).status_code, 302)

    @override_settings(DEBUG=False)
    def test_missing_page_returns_404(self):
        self.assertEqual(self.client.get("/missing-page/").status_code, 404)

    def test_internal_error_returns_500(self):
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        self.assertEqual(custom_500_view(request).status_code, 500)

    def test_player_list_prefetches_team_memberships(self):
        with self.assertNumQueries(2):
            rows = list(PlayerListView.queryset.all())
            for row in rows:
                list(row.teams.all())


class AccountPageTests(TestCase):
    def test_login_page_renders_form_for_visitors(self):
        response = self.client.get(reverse("login"))
        self.assertContains(response, 'name="username"')

    def test_signup_page_renders_form_for_visitors(self):
        response = self.client.get(reverse("signup"))
        self.assertContains(response, 'name="password1"')

    def test_signed_in_user_is_sent_away_from_login_and_signup(self):
        user = User.objects.create_user("demo-coach", password="local-test-password")
        self.client.force_login(user)
        self.assertRedirects(self.client.get(reverse("login")), "/team/")
        self.assertRedirects(self.client.get(reverse("signup")), reverse("home"))


class PlayerFormTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("demo-coach", password="local-test-password")
        self.client.force_login(user)

    def test_player_can_be_saved_without_a_team(self):
        response = self.client.post(
            reverse("player_create"), {"first_name": "Robin", "last_name": "Sample"}
        )
        self.assertRedirects(response, reverse("player_list"))
        self.assertFalse(Player.objects.get(last_name="Sample").teams.exists())

    def test_team_detail_links_each_player(self):
        team = Team.objects.create(city="Harbor", mascot="Gulls")
        player = Player.objects.create(first_name="Jo", last_name="Placeholder")
        player.teams.add(team)
        response = self.client.get(reverse("team_detail", args=[team.pk]))
        self.assertContains(response, reverse("player_detail", args=[player.pk]))
