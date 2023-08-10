from django.core.management.base import BaseCommand
from django.db import transaction

from sports.models import Player, Team

# Invented clubs and athletes for local demos and screenshots. Any resemblance
# to real people is accidental; never replace these with real athletes' data.
DEMO_TEAMS = [
    ("Larkspur", "Harriers"),
    ("Copperfield", "Striders"),
    ("Ashby Vale", "Hurdlers"),
    ("Millbrook", "Comets"),
]

DEMO_PLAYERS = [
    ("Wren", "Halloway", ["Larkspur Harriers"]),
    ("Juno", "Marchetti", ["Larkspur Harriers", "Millbrook Comets"]),
    ("Idris", "Penhallow", ["Copperfield Striders"]),
    ("Sol", "Arkwright", ["Copperfield Striders"]),
    ("Mara", "Quillon", ["Ashby Vale Hurdlers"]),
    ("Teodor", "Vashley", ["Ashby Vale Hurdlers", "Larkspur Harriers"]),
    ("Pip", "Larrabee", ["Millbrook Comets"]),
    ("Odette", "Brannock", ["Millbrook Comets"]),
    ("Kit", "Ferrowby", []),
]


class Command(BaseCommand):
    help = "Load a small fictional league for local demos. Safe to run more than once."

    @transaction.atomic
    def handle(self, *args, **options):
        teams = {}
        for city, mascot in DEMO_TEAMS:
            team, _ = Team.objects.get_or_create(city=city, mascot=mascot)
            teams[str(team)] = team
        created = 0
        for first_name, last_name, team_names in DEMO_PLAYERS:
            player, was_created = Player.objects.get_or_create(
                first_name=first_name, last_name=last_name
            )
            created += was_created
            player.teams.add(*(teams[name] for name in team_names))
        self.stdout.write(
            self.style.SUCCESS(
                f"Demo league ready: {len(teams)} teams, {len(DEMO_PLAYERS)} players "
                f"({created} new)."
            )
        )
