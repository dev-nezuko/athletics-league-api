from io import StringIO

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
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


class DirectoryFeatureTests(TestCase):
    def setUp(self):
        user = User.objects.create_user("demo-coach", password="local-test-password")
        self.client.force_login(user)

    def test_home_summarises_directory_counts(self):
        Player.objects.create(first_name="Ash", last_name="Nobody")
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["player_count"], 1)
        self.assertEqual(response.context["unassigned_count"], 1)

    def test_team_create_update_delete_flow(self):
        self.client.post(reverse("team_create"), {"city": "Fenwick", "mascot": "Foxes"})
        team = Team.objects.get(city="Fenwick")
        self.client.post(
            reverse("team_update", args=[team.pk]), {"city": "Fenwick", "mascot": "Owls"}
        )
        team.refresh_from_db()
        self.assertEqual(team.mascot, "Owls")
        response = self.client.post(reverse("team_delete", args=[team.pk]))
        self.assertRedirects(response, reverse("team_list"))
        self.assertFalse(Team.objects.exists())

    def test_player_update_changes_memberships(self):
        team = Team.objects.create(city="Fenwick", mascot="Foxes")
        player = Player.objects.create(first_name="Ash", last_name="Nobody")
        self.client.post(
            reverse("player_update", args=[player.pk]),
            {"first_name": "Ash", "last_name": "Nobody", "teams": [team.pk]},
        )
        self.assertEqual(list(player.teams.all()), [team])

    def test_player_list_is_paginated(self):
        Player.objects.bulk_create(
            Player(first_name="Demo", last_name=f"Runner {n:02d}") for n in range(30)
        )
        first = self.client.get(reverse("player_list"))
        self.assertEqual(len(first.context["players"]), 25)
        self.assertContains(first, "Page 1 of 2")
        second = self.client.get(reverse("player_list"), {"page": 2})
        self.assertEqual(len(second.context["players"]), 5)

    def test_team_roster_is_sorted_by_surname(self):
        team = Team.objects.create(city="Fenwick", mascot="Foxes")
        for last_name in ("Zeller", "Abbot"):
            Player.objects.create(first_name="Demo", last_name=last_name).teams.add(team)
        response = self.client.get(reverse("team_detail", args=[team.pk]))
        self.assertEqual([p.last_name for p in response.context["roster"]], ["Abbot", "Zeller"])


class SeedDemoCommandTests(TestCase):
    def test_seed_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(Team.objects.count(), 4)
        self.assertEqual(Player.objects.count(), 9)
        self.assertTrue(Player.objects.filter(teams__isnull=True).exists())
