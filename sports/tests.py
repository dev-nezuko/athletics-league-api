from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Team, Player
class RosterTests(TestCase):
    def setUp(self):
        self.user=User.objects.create_user('synthetic-reviewer',password='local-test-password')
        self.client.force_login(self.user)
        self.team=Team.objects.create(city='Northwind',mascot='Owls')
        self.player=Player.objects.create(first_name='Casey',last_name='Example')
        self.player.teams.add(self.team)
    def test_anonymous_lists_require_login(self):
        self.client.logout()
        self.assertRedirects(self.client.get('/team/'),'/login/?next=/team/')
    def test_player_details_render_memberships(self):
        r=self.client.get(reverse('player_detail',args=[self.player.pk]))
        self.assertContains(r,'Northwind');self.assertContains(r,'Casey')
    def test_team_details_render_reverse_membership(self):
        self.assertContains(self.client.get(reverse('team_detail',args=[self.team.pk])),'Casey')
    def test_get_cannot_log_out(self):
        self.assertEqual(self.client.get('/logout/').status_code,405)
        self.assertIn('_auth_user_id',self.client.session)
    def test_logout_requires_csrf_with_real_checks(self):
        client=Client(enforce_csrf_checks=True);client.force_login(self.user)
        self.assertEqual(client.post('/logout/').status_code,403)
        client.get('/team/');token=client.cookies['csrftoken'].value
        self.assertEqual(client.post('/logout/',{'csrfmiddlewaretoken':token}).status_code,302)
    @override_settings(DEBUG=False)
    def test_missing_page_returns_404(self):
        self.assertEqual(self.client.get('/missing-page/').status_code,404)
    def test_internal_error_returns_500(self):
        from .views import custom_500_view
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        request=RequestFactory().get('/');request.user=AnonymousUser()
        self.assertEqual(custom_500_view(request).status_code,500)
    def test_player_list_prefetches_team_memberships(self):
        from .views import PlayerListView
        with self.assertNumQueries(2):
            rows=list(PlayerListView.queryset.all())
            for row in rows:list(row.teams.all())
