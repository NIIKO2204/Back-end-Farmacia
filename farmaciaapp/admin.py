from django.contrib import admin
from .models import Medicamento

# Register your models here.

@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'requiere_receta', 'fecha_ingreso')
    search_fields = ('nombre',)
    list_filter = ('requiere_receta',)