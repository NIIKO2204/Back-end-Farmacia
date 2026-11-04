from django.db import models

class Tarea(models.Model):
    titulo = models.CharField(max_length=35)        
    descripcion = models.CharField(max_length=50)   
    completada = models.BooleanField(default=False)

    def __str__(self):
        return self.titulo