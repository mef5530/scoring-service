from django.shortcuts import render
from rest_framework import viewsets
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .models import Service, Team, Competition, TeamService, ScheduleLock
from .serializers import TeamSerializer, ServiceSerializer, TeamServiceSerializer

class TeamServiceListView(ListView):
    template_name = 'team_service/team_service_list.html'
    context_object_name = 'services'
    model = Service

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)

        context = {
            'teams': [],
            'services': [],
            'status': Competition.objects.first(),
        }

        context['teams'] = list(Team.objects.all())

        for service in Service.objects.all():
            this_service = []
            for team in context['teams']:
                team_service = TeamService.objects.filter(team=team, service=service).first()
                this_service.append(team_service)
            context['services'].append((service, this_service))

        return context

class TeamServiceCreateView(CreateView):
    model = TeamService
    fields = ['id', 'team', 'service', 'uri', 'username', 'password', 'down_checks']
    template_name = 'team_service/team_service_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamServiceUpdateView(UpdateView):
    model = TeamService
    fields = ['id', 'team', 'service', 'uri', 'username', 'password', 'down_checks']
    template_name = 'team_service/team_service_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamServiceDeleteView(DeleteView):
    model = TeamService
    template_name = 'team_service/team_service_delete.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class ServiceCreateView(CreateView):
    model = Service
    fields = ['id', 'name']
    template_name = 'service/service_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class ServiceUpdateView(UpdateView):
    model = Service
    fields = ['id', 'name']
    template_name = 'service/service_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class ServiceDeleteView(DeleteView):
    model = Service
    template_name = 'service/service_delete.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamCreateView(CreateView):
    model = Team
    fields = ['id', 'name', 'score', 'max_score']
    template_name = 'team/team_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamUpdateView(UpdateView):
    model = Team
    fields = ['id', 'name', 'score', 'max_score']
    template_name = 'team/team_form.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'team/team_delete.html'

    def get_success_url(self):
        return reverse_lazy('team-services')

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class TeamServiceViewSet(viewsets.ModelViewSet):
    queryset = TeamService.objects.all()
    serializer_class = TeamServiceSerializer

@require_POST
def start_comp(request):
    comp = Competition.objects.get_or_create(id=1)[0]
    comp.paused = False
    comp.save()
    schedule_lock = ScheduleLock.objects.all().filter(id=1).first()
    schedule_lock.locked = False
    schedule_lock.save()
    return JsonResponse({'status': 'success'})

@require_POST
def stop_comp(request):
    comp = Competition.objects.get_or_create(id=1)[0]
    comp.paused = True
    comp.save()
    return JsonResponse({'status': 'success'})
