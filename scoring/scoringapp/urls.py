from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamServiceListView, TeamViewSet, ServiceViewSet, TeamServiceViewSet, TeamServiceCreateView, TeamServiceUpdateView, TeamUpdateView, TeamCreateView, ServiceUpdateView, ServiceCreateView, TeamServiceDeleteView, ServiceDeleteView, TeamDeleteView, start_comp, stop_comp

router = DefaultRouter()
router.register(r'teams', TeamViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'team-services', TeamServiceViewSet)

urlpatterns = [
    path('team_services/', TeamServiceListView.as_view(), name='team-services'),
    path('comp/', include(router.urls)),
    path('team_service/create/', TeamServiceCreateView.as_view(), name='team-service-create'),
    path('team_service/update/<int:pk>/', TeamServiceUpdateView.as_view(), name='team-service-update'),
    path('team_service/delete/<int:pk>/', TeamServiceDeleteView.as_view(), name='team-service-delete'),
    path('team/create/', TeamCreateView.as_view(), name='team-create'),
    path('team/update/<int:pk>/', TeamUpdateView.as_view(), name='team-update'),
    path('team/delete/<int:pk>/', TeamDeleteView.as_view(), name='team-delete'),
    path('service/create/', ServiceCreateView.as_view(), name='service-create'),
    path('service/update/<int:pk>/', ServiceUpdateView.as_view(), name='service-update'),
    path('service/delete/<int:pk>/', ServiceDeleteView.as_view(), name='service-delete'),
    path('comp/start/', start_comp, name='start-comp'),
    path('comp/stop/', stop_comp, name='stop-comp'),
]