from django.core.management.base import BaseCommand
from django.db import connections
import requests
import time
import datetime
import tftpy
from tftpy import TftpFileNotFoundError
from paramiko import SSHClient, AutoAddPolicy
import mysql.connector
from mysql.connector import Error
import ldap3
import dns.resolver
import ping3
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import subprocess
import pytz

from scoringapp.models import TeamService, Check, Team

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'check the services'

    def handle(self, *args, **kwargs):
        start_time = time.time()
        team_services = TeamService.objects.all()

        for team_service in team_services:
            self.perform_check(team_service)

        # with ThreadPoolExecutor(max_workers=20) as executor:
        #     futures = {
        #         executor.submit(self.perform_check, team_service): team_service for team_service in team_services
        #     }
        #     for future in as_completed(futures):
        #         team_service = futures[future]
        #         try:
        #             future.result()
        #         except Exception as e:
        #             logging.error(f'Error checking {team_service.uri}: {e}')

        total_time = time.time() - start_time
        logging.debug(f"Total execution time: {total_time:.2f} seconds.")
    
    def check_http(self, host, path, timeout=2) -> (bool, str):
        try:
            response = requests.get(f'http://{host}/{path}', timeout=timeout)
            if response.status_code == 200 or response.status_code == 404 or response.status_code == 302:
                return (True, 'up')
            else:
                return (False, f'response code = {response.status_code}')
        except Exception as e:
            return (False, f'request failed with: {e}')

    def check_https(self, host, path, timeout=2) -> (bool, str):
        try:
            response = requests.get(f'https://{host}/{path}', timeout=timeout, verify=False)
            if response.status_code == 200 or response.status_code == 404 or response.status_code == 302:
                return (True, 'up')
            else:
                return (False, f'response code = {response.status_code}')
        except Exception as e:
            return (False, f'request failed with: {e}')

    def check_ssh(self, host, username, password, timeout=2) -> (bool, str):
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(AutoAddPolicy())
            client.connect(host, username=username, password=password, timeout=timeout)
            client.close()
            return (True, 'up')
        except Exception as e:
            return (False, f'connection failed with: {e}')

    def check_tftp(self, host, timeout=2, retries=0) -> (bool, str):
        try:
            client = tftpy.TftpClient(host)
            client.download('greyteamfile', 'greyteamfile', timeout=timeout, retries=retries)
            return (True, 'up')
        except TftpFileNotFoundError:
            return (True, 'up')
        except Exception as e:
            return (False, f'connection failed with: {e}')

    def check_mysql(self, host, username, password, timeout=2) -> (bool, str):
        try:
            connection = mysql.connector.connect(
                host=host,
                user=username,
                password=password,
                connection_timeout=timeout,
                auth_plugin='mysql_native_password',
            )
            if connection.is_connected():
                connection.close()
                return (True, 'up')
            else:
                return (False, 'connection failed')
        except Exception as e:
            return (False, f'connection failed with: {e}')

    def check_ldap(self, host, username, password, timeout=2) -> (bool, str):
        try:
            server = ldap3.Server(host, connect_timeout=timeout)
            conn = ldap3.Connection(server, user=username, password=password, auto_bind=True)
            conn.unbind()
            return (True, 'up')
        except Exception as e:
            return (False, f'connection failed with: {e}')

    def check_dns(self, host, timeout=2) -> (bool, str):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [host]
            resolver.timeout = timeout
            resolver.lifetime = timeout
            answers = resolver.resolve('google.com', 'A')
            if answers:
                return (True, 'up')
            else:
                return (False, 'no DNS response')
        except Exception as e:
            return (False, f'DNS query failed with: {e}')

    def check_icmp(self, host, timeout=1) -> (bool, str):
        try:
            command = ['ping', '-c', '1', '-W', str(timeout), host]
            output = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            if output.returncode == 0:
                return (True, 'up')
            else:
                return (False, f'no response: {output.stderr.strip()}')
        except Exception as e:
            return (False, f'ping failed with: {e}')

    def perform_check(self, team_service):
        db = connections['default']
        db.close_if_unusable_or_obsolete()

        start_time = time.time()
        toks = team_service.uri.split('$')
        if len(toks) < 2:
            logging.error(f'Invalid URI format for team_service id {team_service.id}')
            return
        service_type = toks[0]
        host = toks[1]

        is_up = False
        status = 'Unknown error'

        try:
            if service_type == 'http':
                if len(toks) < 3:
                    logging.error(f'Invalid URI format for HTTP service, missing path for team_service id {team_service.id}')
                    return
                path = toks[2]
                is_up, status = self.check_http(host=host, path=path)
            elif service_type == 'https':
                if len(toks) < 3:
                    logging.error(f'Invalid URI format for HTTP service, missing path for team_service id {team_service.id}')
                    return
                path = toks[2]
                is_up, status = self.check_https(host=host, path=path)
            elif service_type == 'ssh':
                is_up, status = self.check_ssh(host=host, username=team_service.username, password=team_service.password)
            elif service_type == 'tftp':
                is_up, status = self.check_tftp(host=host)
            elif service_type == 'mysql':
                is_up, status = self.check_mysql(host=host, username=team_service.username, password=team_service.password)
            elif service_type == 'ldap':
                is_up, status = self.check_ldap(host=host, username=team_service.username, password=team_service.password)
            elif service_type == 'dns':
                is_up, status = self.check_dns(host=host)
            elif service_type == 'icmp':
                is_up, status = self.check_icmp(host=host)
            else:
                logging.error(f'Unknown service type "{service_type}" for team_service id {team_service.id}')
                return

            check = Check(
                team_service=team_service, 
                time=datetime.datetime.now(tz=pytz.timezone('US/Eastern')), 
                is_up=is_up, 
                status=status
            )
            check.save()

            cur_team_service = TeamService.objects.filter(id=team_service.id).first()
            cur_team_service.newest_check = check

            team = Team.objects.filter(id=team_service.team.id).first()
            team.max_score += 1

            if is_up:
                logging.info(f'Service {service_type} on {host} is up.')
                team.score += 1
                cur_team_service.down_checks = 0
            else:
                logging.info(f'Service {service_type} on {host} is down: {status}')
                cur_team_service.down_checks += 1
                if cur_team_service.down_checks < 5:
                    team.score += 1

            team.save()
            cur_team_service.save()
            
        except Exception as e:
            logging.error(f'Error checking service {service_type} on {host}: {e}')
        finally:
            elapsed_time = time.time() - start_time
            logging.debug(f"Check for service {service_type} on {host} took {elapsed_time:.2f} seconds.")
