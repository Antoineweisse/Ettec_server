from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
# Create your models here.

class EmployeeManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Users must have an login')
        user = self.model(
            login=login,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(login, password, **extra_fields)

class Employee(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=100,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(unique=False, null=True, blank=True)
    formations = models.ManyToManyField('Formation', blank=True)
    btp_card = models.ImageField(upload_to='btp_cards/', null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    lastname = models.CharField(max_length=100, null=True, blank=True)
    contrat = models.CharField(max_length=100, null=True, blank=True)
    telephone = models.CharField(max_length=100, null=True, blank=True)

    objects = EmployeeManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.login
    
    def delete(self, *args, **kwargs):
        if self.btp_card:
            try:
                self.btp_card.delete(save=False)
            except Exception as e:
                print(f"Error deleting BTP card file: {e}")
        super().delete(*args, **kwargs)


class Zone(models.Model):
    villes = models.CharField(max_length=100)
    dept = models.CharField(max_length=100)
    zone = models.CharField(max_length=100)
    km = models.IntegerField()

    def __str__(self):
        return self.villes
    
class Chantier(models.Model):
    name = models.CharField(max_length=100)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Presence(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)
    chantier = models.ForeignKey(Chantier, on_delete=models.CASCADE, null=True, blank=True)
    collaborateurs = models.ManyToManyField(Employee, related_name="presences_collaborateur", blank=True)
    interimaire = models.IntegerField()
    heures = models.FloatField()

    def __str__(self):
        return f"{self.employee.login} - {self.date} - {self.status}"
    

class PhotoChantier(models.Model):
    chantier = models.ForeignKey(Chantier, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')
    date = models.DateTimeField()
    expediteur = models.ForeignKey(Employee, on_delete=models.CASCADE)
    has_been_downloaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Photo for {self.chantier.name} by {self.expediteur.login} on {self.date}"
    
    def delete(self, *args, **kwargs):
        if self.photo:
            try:
                self.photo.delete(save=False)
            except Exception as e:
                print(f"Error deleting photo file: {e}")
        super().delete(*args, **kwargs)

class DocumentsChantier(models.Model):
    chantier = models.ForeignKey(Chantier, on_delete=models.CASCADE)
    document = models.FileField(upload_to='documents/')
    name= models.CharField(max_length=100)

    def __str__(self):
        return f"Document {self.document.name} for {self.chantier.name}"
    
    def delete(self, *args, **kwargs):
        if self.document:
            try:
                self.document.delete(save=False)
            except Exception as e:
                print(f"Error deleting document file: {e}")
        super().delete(*args, **kwargs)

class Formation(models.Model):
    name= models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/formations/')

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        if self.file:
            try:
                self.file.delete(save=False)
            except Exception as e:
                print(f"Error deleting formation file: {e}")
        super().delete(*args, **kwargs)

class StatusTravail(models.Model):
    name = models.CharField(max_length=100)
    raccourcis = models.CharField(max_length=10)

    def __str__(self):
        return self.name