from django.urls import path
from . import views


urlpatterns = [
    # Pagina principal de login
    path('', views.login_pagina, name='login_pagina'),

    # Vistas web tradicionales (HTML) de Farmacia
    path('medicamentos/', views.inicio, name='inicio'),
    path('crear/', views.crear_medicamento, name='crear_medicamento'),
    path('detalle/<int:id>/', views.detalle_medicamento, name='detalle_medicamento'),
    path('editar/<int:id>/', views.editar_medicamento, name='editar_medicamento'),
    path('eliminar/<int:id>/', views.eliminar_medicamento, name='eliminar_medicamento'),

    # API REST para autenticación por Token
    path('api/login/', views.LoginAPIView.as_view(), name='login_api'),

    # API REST para listar y crear medicamentos
    path('api/medicamentos/', views.MedicamentosApiView.as_view(), name='api_medicamentos'),

    # API REST Detalle (Consultar y Eliminar) un medicamento por ID
    path('api/medicamentos/<int:id>/', views.MedicamentoDetalleApiView.as_view(), name='api_medicamento_detalle'),
]