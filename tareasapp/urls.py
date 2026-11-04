from django.contrib import admin
from django.urls import path
from tareasapp import views

urlpatterns = [
    # Vistas tradicionales (HTML)
    path('', views.login_pagina, name='login'),
    path('tareas/', views.inicio, name='inicio'),
    path('crear/', views.crear_tarea, name='crear_tarea'),
    path('detalle/<int:id>/', views.detalle_tarea, name='detalle_tarea'),
    path('editar/<int:id>/', views.editar_tarea, name='editar_tarea'),
    path('eliminar/<int:id>/', views.eliminar_tarea, name='eliminar_tarea'),

    # Rutas de la API REST (¡Estas eran las que faltaban!)
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('api/tareas/', views.TareasApiView.as_view(), name='api_tareas'),
    path('api/tareas/<int:id>/', views.TareaDetalleApiView.as_view(), name='api_tarea_detalle'),
]