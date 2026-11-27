from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # LOGIN Y SESION WEB
    path("", views.login_pagina, name="login_pagina"),
    path("web/login/", views.login_web, name="login_web"),
    path("web/logout/", views.cerrar_sesion, name="cerrar_sesion"),
    # PAGINAS DE MEDICAMENTOS
    path("medicamentos/", views.inicio, name="inicio"),
    path("crear/", views.crear_medicamento, name="crear_medicamento"),
    path("detalle/<int:id>/", views.detalle_medicamento, name="detalle_medicamento"),
    path("editar/<int:id>/", views.editar_medicamento, name="editar_medicamento"),
    path("eliminar/<int:id>/", views.eliminar_medicamento, name="eliminar_medicamento"),
    # API REST - MEDICAMENTOS
    path("api/medicamentos/", views.MedicamentosApiView.as_view(), name="api_medicamentos"),
    path(
        "api/medicamentos/<int:id>/",
        views.MedicamentoDetalleApiView.as_view(),
        name="api_medicamento_detalle",
    ),
    # JWT - GENERAR Y RENOVAR TOKENS
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # DOCUMENTACION SWAGGER / OPENAPI
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]