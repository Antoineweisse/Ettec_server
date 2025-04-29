from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


router = DefaultRouter()

router.register(r'employees', views.EmployeeViewSet, basename='employee')
router.register(r'zones', views.ZoneViewSet, basename='zone')
router.register(r'chantiers', views.ChantierViewSet, basename='chantier')
router.register(r'presences', views.PresenceViewSet, basename='presence')
router.register(r'photos_chantier', views.PhotoChantierViewSet, basename='photo-chantier')
router.register(r'documents_chantier', views.DocumentsChantierViewSet, basename='documents-chantier')
router.register(r'formations', views.FormationViewSet, basename='formation')

urlpatterns = [
    # Endpoints pour les employés
    path('',include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('export/excel/', views.get_excel, name='excel'),
]
