from rest_framework import serializers
from .models import *

class EmployeeSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Employee
        fields = '__all__'

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        formations = validated_data.pop('formations', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        if formations is not None:
            instance.formations.set(formations)

        instance.save()
        return instance
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        formations = validated_data.pop('formations', [])
        groups = validated_data.pop('groups', [])
        user_permissions = validated_data.pop('user_permissions', [])

        user = Employee(**validated_data)
        user.set_password(password)
        user.save()

        if formations:
            user.formations.set(formations)

        user.groups.set(groups)
        user.user_permissions.set(user_permissions)

        return user

class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = '__all__'

class ChantierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chantier
        fields = '__all__'

class PresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presence
        fields = '__all__'

class PhotoChantierSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField()

    class Meta:
        model = PhotoChantier
        fields = '__all__'

class DocumentsChantierSerializer(serializers.ModelSerializer):
    document = serializers.FileField()

    class Meta:
        model = DocumentsChantier
        fields = '__all__'

class FormationSerializer(serializers.ModelSerializer):
    file = serializers.FileField()

    class Meta:
        model = Formation
        fields = '__all__'