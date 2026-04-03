from django.db import models

class Profile(models.Model):
    # Relaciona el ID único que Laravel le asigna al usuario
    user_id = models.IntegerField(unique=True) 
    #Información del usuario que laravel no guarda pero sí django
    bio = models.TextField(max_length=500, blank=True, null=True) #Biografía
    phone = models.CharField(max_length=20, blank=True, null=True) #Número telefónico
    address = models.CharField(max_length=255, blank=True, null=True) #Dirección

    def __str__(self):
        return f"Perfil del Usuario ID: {self.user_id}"
