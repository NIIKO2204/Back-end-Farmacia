from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_medicamento, name='crear_medicamento'),
    path('detalle/<int:id>/', views.detalle_medicamento, name='detalle_medicamento'),
    path('editar/<int:id>/', views.editar_medicamento, name='editar_medicamento'),
    path('eliminar/<int:id>/', views.eliminar_medicamento, name='eliminar_medicamento'),
]