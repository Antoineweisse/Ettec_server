from django.contrib import admin
from .models import *
from .forms import EmployeeCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class EmployeeAdmin(BaseUserAdmin):
    add_form = EmployeeCreationForm
    list_display = ('id', 'login', 'is_active', 'is_staff','is_superuser', 'formations_list','btp_card', 'name', 'lastname', 'email', 'contrat')
    search_fields = ('login',)
    list_filter = ('login',)
    ordering = ('login',)
    list_per_page = 10

    fieldsets = (
        (None, {'fields': ('login', 'email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser'),
        }),
    )

    def formations_list(self, obj):
        return ", ".join([formation.name for formation in obj.formations.all()])

class ZoneAdmin(admin.ModelAdmin):
    list_display = ('villes', 'dept', 'zone', 'km')
    search_fields = ('villes',)
    list_filter = ('villes',)
    ordering = ('villes',)
    list_per_page = 10

class ChantierAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    list_per_page = 10

class PresenceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'status', 'chantier', 'interimaire', 'heures', 'collaborateurs_name')
    search_fields = ('employee__login',)
    list_filter = ('employee',)
    ordering = ('employee',)
    list_per_page = 10

    def collaborateurs_name(self, obj):
        return ", ".join([collaborateur.login for collaborateur in obj.collaborateurs.all()])

class PhotoChantierAdmin(admin.ModelAdmin):
    list_display = ('chantier', 'photo', 'date', 'expediteur')
    search_fields = ('chantier__name',)
    list_filter = ('chantier',)
    ordering = ('chantier',)
    list_per_page = 10

class DocumentsChantierAdmin(admin.ModelAdmin):
    list_display = ('chantier', 'document', 'name')
    search_fields = ('chantier__name',)
    list_filter = ('chantier',)
    ordering = ('chantier',)
    list_per_page = 10

class FormationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','file')
    search_fields = ('name',)
    list_filter = ('name',)
    ordering = ('name',)
    list_per_page = 10

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Zone, ZoneAdmin)
admin.site.register(Chantier, ChantierAdmin)
admin.site.register(Presence, PresenceAdmin)
admin.site.register(PhotoChantier, PhotoChantierAdmin)
admin.site.register(DocumentsChantier, DocumentsChantierAdmin)
admin.site.register(Formation, FormationAdmin)