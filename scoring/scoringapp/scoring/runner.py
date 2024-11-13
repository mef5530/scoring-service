from django.core.management.base import BaseCommand
import requests
import time
import tftpy
from tftpy import TftpFileNotFoundError
from paramiko import SSHClient, AutoAddPolicy

from scoringapp.models import TeamService, Check, Competition

def check_html(host, path, timeout=5) -> (bool, str):
    try:
        response = requests.get(f'http://{host}/{path}', timeout=timeout)
        if response.status_code == 200:
            return (True, 'up')
        else:
            return (False, f'response code = {response.status_code}')
    except Exception as e:
        return (False, f'request failed with: {e}')

def check_ssh(host, username, password) -> (bool, str):
    try:
        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        client.connect(host, username=username, password=password)
        client.close()
        return (True, 'up')
    except Exception as e:
        return (False, f'connection failed with: {e}')

def check_tftp(host) -> (bool, str):
    try:
        client = tftpy.TftpClient(host)
        client.download('greyteamfile', 'greyteamfile', timeout=2, retries=1)
        return (True, 'up')
    except TftpFileNotFoundError as e:
        return (True, 'up')
    except Exception as e:
        return (False, f'connection failed with: {e}')



class CheckAll(BaseCommand):
    
    def handle(self, *args, **kwargs):
        team_services = TeamService.objects.all()
        for team_service in team_services:
            toks = team_service.uri.split('$')
            if toks[0] == 'http':
                is_up, status = check_html(host=toks[1], path=toks[2])
            elif toks[0] == 'ssh':
                is_up, status = check_ssh(host=toks[1], username=team_service.username, password=team_service.password)
            elif toks[0] == 'tftp':
                is_up, status = check_tftp(host=toks[1])
            elif toks[0] == 'mysql':
                pass
            elif toks[0] == 'ldap':
                pass
            elif toks[0] == 'dns':
                pass
            elif toks[0] == 'icmp':
                pass
            check = Check(team_service=team_service, 
                          time=time.time, 
                          is_up=is_up, 
                          status=status)
            check.save()
