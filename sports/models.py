from django.db import models

class Team(models.Model):
    city = models.CharField(max_length=100)
    mascot = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} {self.mascot}"

class Player(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teams = models.ManyToManyField(Team)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"