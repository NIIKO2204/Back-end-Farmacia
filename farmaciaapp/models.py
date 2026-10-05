from django.db import models

class Medicamento(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.IntegerField(default=0)
    stock = models.IntegerField(default=0)
    requiere_receta = models.BooleanField(default=False)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"