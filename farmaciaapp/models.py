from django.db import models

class Medicamento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    requiere_receta = models.BooleanField(default=False)
    fecha_ingreso = models.DateField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.nombre