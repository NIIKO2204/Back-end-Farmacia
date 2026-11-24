import json
from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.views.decorators.http import require_POST

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication, SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError

from .models import Medicamento

# =====================================================
# AUTENTICACION WEB MEDIANTE SESION DJANGO
# =====================================================


def sesion_web_requerida(vista):
    """
    Comprueba que exista una sesión web válida.
    Renueva el Access Token cuando expira.
    """

    @wraps(vista)
    def funcion(request, *args, **kwargs):

        access = request.session.get("access")
        refresh = request.session.get("refresh")

        if not access or not refresh:
            request.session.flush()
            return redirect("/")

        try:
            AccessToken(access)

        except TokenError:
            try:
                serializer = TokenRefreshSerializer(data={"refresh": refresh})
                serializer.is_valid(raise_exception=True)

                nuevos_tokens = serializer.validated_data

                request.session["access"] = nuevos_tokens["access"]

                if "refresh" in nuevos_tokens:
                    request.session["refresh"] = nuevos_tokens["refresh"]

            except Exception:
                request.session.flush()
                return redirect("/")

        return vista(request, *args, **kwargs)

    return funcion


# =====================================================
# AUTENTICACION JWT DESDE LA SESION WEB
# =====================================================


class SessionJWTAuthentication(BaseAuthentication):
    """
    Permite que las API REST utilicen el JWT almacenado
    en la sesión Django cuando no reciben un Bearer Token.

    También renueva automáticamente el Access Token.
    """

    def authenticate(self, request):

        access = request.session.get("access")
        refresh = request.session.get("refresh")

        # Si no hay sesión JWT, permite continuar con
        # el siguiente método de autenticación.
        if not access and not refresh:
            return None

        if not access or not refresh:
            request.session.flush()
            raise AuthenticationFailed("Sesión expirada. Inicia sesión nuevamente.")

        # Exigir CSRF cuando se utiliza autenticación por sesión.
        SessionAuthentication().enforce_csrf(request)

        jwt_auth = JWTAuthentication()

        try:
            validated_token = jwt_auth.get_validated_token(access)

        except TokenError:
            # Access vencido: intentar renovar con Refresh.
            try:
                serializer = TokenRefreshSerializer(data={"refresh": refresh})
                serializer.is_valid(raise_exception=True)

                nuevos_tokens = serializer.validated_data

                request.session["access"] = nuevos_tokens["access"]

                if "refresh" in nuevos_tokens:
                    request.session["refresh"] = nuevos_tokens["refresh"]

                validated_token = jwt_auth.get_validated_token(
                    request.session["access"]
                )

            except Exception:
                request.session.flush()
                raise AuthenticationFailed(
                    "Tu sesión ha expirado. Inicia sesión nuevamente."
                )

        try:
            usuario = jwt_auth.get_user(validated_token)

            if not usuario.is_active:
                request.session.flush()
                raise AuthenticationFailed("Usuario desactivado.")

        except AuthenticationFailed:
            request.session.flush()
            raise

        return (usuario, validated_token)


# =====================================================
# LOGIN WEB
# =====================================================


def login_pagina(request):

    if request.session.get("access") and request.session.get("refresh"):
        return redirect("/medicamentos/")

    return render(request, "farmaciaapp/login.html")


@require_POST
def login_web(request):

    try:
        datos = json.loads(request.body)

        username = datos.get("username")
        password = datos.get("password")

        if not username or not password:
            return JsonResponse(
                {"error": "Debes ingresar usuario y contraseña"}, status=400
            )

        usuario = authenticate(request, username=username, password=password)

        if usuario is None:
            return JsonResponse(
                {"error": "Usuario o contraseña incorrectos"}, status=401
            )

        if not usuario.is_active:
            return JsonResponse({"error": "La cuenta está desactivada"}, status=403)

        # Generar JWT.
        refresh = RefreshToken.for_user(usuario)

        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        # Crear una nueva sesión Django.
        request.session.flush()

        request.session["access"] = access_token
        request.session["refresh"] = refresh_token
        request.session["usuario"] = usuario.username

        # Expiración de sesión: 30 minutos.
        request.session.set_expiry(1800)

        return JsonResponse(
            {"mensaje": "Inicio de sesión correcto", "usuario": usuario.username}
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Solicitud JSON inválida"}, status=400)


# =====================================================
# CERRAR SESION
# =====================================================


@require_POST
def cerrar_sesion(request):

    refresh = request.session.get("refresh")

    if refresh:
        try:
            token = RefreshToken(refresh)
            token.blacklist()

        except TokenError:
            pass

    # Destruir la sesión Django.
    request.session.flush()

    return JsonResponse({"mensaje": "Sesión cerrada correctamente"})


# =====================================================
# VISTAS HTML PROTEGIDAS
# =====================================================


@sesion_web_requerida
def inicio(request):
    return render(request, "farmaciaapp/inicio.html")


@sesion_web_requerida
def crear_medicamento(request):
    return render(request, "farmaciaapp/crear.html")


@sesion_web_requerida
def detalle_medicamento(request, id):
    return render(request, "farmaciaapp/detalle.html")


@sesion_web_requerida
def editar_medicamento(request, id):
    return render(request, "farmaciaapp/editar.html")


@sesion_web_requerida
def eliminar_medicamento(request, id):
    return render(request, "farmaciaapp/eliminar.html")


# =====================================================
# API REST - MEDICAMENTOS
# ACEPTA JWT BEARER Y JWT DESDE SESION WEB
# =====================================================


class MedicamentosApiView(APIView):

    authentication_classes = [JWTAuthentication, SessionJWTAuthentication]

    permission_classes = [IsAuthenticated]

    # GET: listar todos los medicamentos.
    def get(self, request):

        medicamentos = Medicamento.objects.all()

        datos = []

        for medicamento in medicamentos:
            datos.append(
                {
                    "id": medicamento.id,
                    "nombre": medicamento.nombre,
                    "descripcion": medicamento.descripcion,
                    "precio": medicamento.precio,
                    "stock": medicamento.stock,
                    "disponible": medicamento.disponible,
                }
            )

        return Response(datos, status=status.HTTP_200_OK)

    # POST: crear un nuevo medicamento.
    def post(self, request):

        nombre = request.data.get("nombre")
        descripcion = request.data.get("descripcion")
        precio = request.data.get("precio")
        stock = request.data.get("stock")
        disponible = request.data.get("disponible", True)

        if (
            not nombre
            or not descripcion
            or precio is None
            or stock is None
        ):
            return Response(
                {
                    "error": "El nombre, la descripcion, el precio y el stock son obligatorios"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicamento = Medicamento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            disponible=disponible,
        )

        return Response(
            {
                "mensaje": "Medicamento creado correctamente",
                "medicamento": {
                    "id": medicamento.id,
                    "nombre": medicamento.nombre,
                    "descripcion": medicamento.descripcion,
                    "precio": medicamento.precio,
                    "stock": medicamento.stock,
                    "disponible": medicamento.disponible,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class MedicamentoDetalleApiView(APIView):

    authentication_classes = [JWTAuthentication, SessionJWTAuthentication]

    permission_classes = [IsAuthenticated]

    # GET: consultar medicamento por ID.
    def get(self, request, id):

        medicamento = get_object_or_404(Medicamento, id=id)

        return Response(
            {
                "id": medicamento.id,
                "nombre": medicamento.nombre,
                "descripcion": medicamento.descripcion,
                "precio": medicamento.precio,
                "stock": medicamento.stock,
                "disponible": medicamento.disponible,
            },
            status=status.HTTP_200_OK,
        )

    # DELETE: eliminar medicamento.
    def delete(self, request, id):

        medicamento = get_object_or_404(Medicamento, id=id)
        medicamento.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT: actualizar todos los campos.
    def put(self, request, id):

        medicamento = get_object_or_404(Medicamento, id=id)

        nombre = request.data.get("nombre")
        descripcion = request.data.get("descripcion")
        precio = request.data.get("precio")
        stock = request.data.get("stock")
        disponible = request.data.get("disponible")

        if (
            nombre is None
            or descripcion is None
            or precio is None
            or stock is None
            or disponible is None
        ):
            return Response(
                {"error": "Debes enviar todos los campos"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(nombre, str) or not nombre.strip():
            return Response(
                {"error": "El nombre es obligatorio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicamento.nombre = nombre
        medicamento.descripcion = descripcion
        medicamento.precio = precio
        medicamento.stock = stock
        medicamento.disponible = disponible
        medicamento.save()

        return Response(
            {
                "mensaje": "Medicamento actualizado correctamente",
                "id": medicamento.id,
                "nombre": medicamento.nombre,
                "descripcion": medicamento.descripcion,
                "precio": medicamento.precio,
                "stock": medicamento.stock,
                "disponible": medicamento.disponible,
            },
            status=status.HTTP_200_OK,
        )