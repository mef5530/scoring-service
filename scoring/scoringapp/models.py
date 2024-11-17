from django.db import models

class ScheduleLock(models.Model):
    id = models.AutoField(primary_key=True)
    locked = models.BooleanField(default=False)

class Competition(models.Model):
    id = models.AutoField(primary_key=True)
    paused = models.BooleanField(default=True)

class Team(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)

    def repr(self):
        return f'Team({self.name})'

class Service(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)

    def repr(self):
        return f'Service({self.name})'

class TeamService(models.Model):
    id = models.AutoField(primary_key=True)
    team = models.ForeignKey('Team', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    uri = models.CharField(max_length=1024)
    username = models.CharField(max_length=255, blank=True)
    password = models.CharField(max_length=255, blank=True)
    newest_check = models.ForeignKey('Check', null=True, on_delete=models.SET_NULL)
    down_checks = models.IntegerField(default=0)

class Check(models.Model):
    id = models.AutoField(primary_key=True)
    team_service = models.ForeignKey('TeamService', on_delete=models.CASCADE)
    time = models.DateTimeField()
    is_up = models.BooleanField()
    status = models.CharField(max_length=1024, blank=True)