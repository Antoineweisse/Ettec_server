from datetime import date
from rest_framework import viewsets
from .models import Employee, Zone, Chantier, Presence
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import pillow_heif
import os
pillow_heif.register_heif_opener()

from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import action

from .excel import MakeExcel
from rest_framework.decorators import api_view
from django.http import HttpResponse
from collections import defaultdict

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return Employee.objects.filter(is_superuser=False)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='me/formations')
    def me_formations(self, request):
        user = request.user
        formations = Formation.objects.filter(employee=user)
        serializer = FormationSerializer(formations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get','post'], url_path='me/presences')
    def me_presences(self, request):
        user = request.user
        if request.method == 'GET':
            week_number = int(request.query_params.get('week', date.today().isocalendar()[1]))
            year = int(request.query_params.get('year', date.today().year))
            presences = Presence.objects.filter(
                employee=user, 
                date__week=week_number, 
                date__year=year
            ).order_by('date')
            serializer = PresenceSerializer(presences, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            data = request.data.copy()
            data['employee'] = user.id
            serializer = PresenceSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='formations')
    def formations(self, request, pk=None):
        formations = Formation.objects.filter(employee=pk)
        serializer = FormationSerializer(formations, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='presences')
    def presences(self, request, pk=None):
        presences = Presence.objects.filter(employee=pk)
        serializer = PresenceSerializer(presences, many=True, context={'request': request})
        return Response(serializer.data)

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class ChantierViewSet(viewsets.ModelViewSet):
    queryset = Chantier.objects.all()
    serializer_class = ChantierSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @action(detail=True, methods=['get'], url_path='photos')
    def chantier_photos(self, request, pk=None):
        chantier = self.get_object()
        photos = chantier.photochantier_set.all()
        serializer = PhotoChantierSerializer(photos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='documents')
    def chantier_documents(self, request, pk=None):
        chantier = self.get_object()
        documents = chantier.documentschantier_set.all()
        serializer = DocumentsChantierSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)

class PresenceViewSet(viewsets.ModelViewSet):
    queryset = Presence.objects.all()
    serializer_class = PresenceSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    

class DocumentsChantierViewSet(viewsets.ModelViewSet):
    queryset = DocumentsChantier.objects.all()
    serializer_class = DocumentsChantierSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class FormationViewSet(viewsets.ModelViewSet):
    queryset = Formation.objects.all()
    serializer_class = FormationSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

class PhotoChantierViewSet(viewsets.ModelViewSet):
    queryset = PhotoChantier.objects.all()
    serializer_class = PhotoChantierSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def convert_heic_to_jpg(self, heic_file):
        try:
            image = Image.open(heic_file)
            rgb_image = image.convert('RGB')
            buffer = BytesIO()
            rgb_image.save(buffer, format='JPEG')
            buffer.seek(0)
            new_file = ContentFile(buffer.read())
            new_file.name = os.path.splitext(heic_file.name)[0] + '.jpg'
            new_file.content_type = 'image/jpeg'
            return new_file
        except Exception as e:
            return None

    def create(self, request, *args, **kwargs):
        files = request.FILES.getlist('photo')
        if not files:
            return Response({"error": "Aucun fichier fourni."}, status=status.HTTP_400_BAD_REQUEST)
    
       
        created_files = []
        for file in files:
            if file.content_type in ['application/octet-stream', 'image/heic', 'image/heif']:
                converted_file = self.convert_heic_to_jpg(file)
                if converted_file:
                    file = converted_file
                else:
                    return Response({"error": "Échec de la conversion de l'image."}, status=status.HTTP_400_BAD_REQUEST)
                
            data = {
                'chantier': request.data.get('chantier'),
                'expediteur': request.user.id,
                'date': request.data.get('date'),
                'photo': file
            }
            serializers = self.get_serializer(data=data)
            serializers.is_valid(raise_exception=True)
            self.perform_create(serializers)
            created_files.append(serializers.data)

        return Response(created_files, status=status.HTTP_201_CREATED)
    

class CookieTokenObtainPairView(TokenObtainPairView):
    def post(self,request,*args,**kwargs):
        response = super().post(request,*args,**kwargs)
        if response.status_code == 200:
            refresh = response.data.get('refresh')

            del response.data['refresh']

            response.set_cookie(
                key='refresh',
                value=refresh,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=60*60*24*7, # 1 week
                path='/api/token/refresh/' # Adjust the path as needed
            )

        return response
    

class CookieTokenRefreshView(TokenRefreshView):
    def post(self,request,*args,**kwargs):
        refresh_token = request.COOKIES.get('refresh')

        if refresh_token is None:
            return AuthenticationFailed('Refresh token not found in cookies.')
        
        request.data['refresh'] = refresh_token
        return super().post(request,*args,**kwargs)
    

@api_view(['GET'])
def get_excel(request):
    year = int(request.query_params.get('year', date.today().year))
    month = int(request.query_params.get('month', date.today().month))

    employees = Employee.objects.filter(is_superuser=False)

    dictionnary = {}
    for employee in employees:
        presences = Presence.objects.filter(date__year=year, date__month=month, employee=employee)
        dictionnary[employee.id] = {
            'name': employee.name,
            'lastname': employee.lastname,
            'contrat': employee.contrat,
            'presences':  [
                {
                    'date': presence.date,
                    'status': presence.status,
                    'zone': presence.chantier.zone.zone if presence.chantier and presence.chantier.zone else None,
                    'heures': presence.heures
                }
                for presence in presences
            ]
        }

    # Generate the Excel file
    excel_file = MakeExcel(dictionnary)
    
    # # Return the Excel file as a response
    response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="presences_{month}_{year}.xlsx"'
    response["Access-Control-Expose-Headers"] = "Content-Disposition"
    return response