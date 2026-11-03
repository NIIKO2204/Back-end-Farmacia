from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Medicamento

# --- VISTAS WEB TRADICIONALES (HTML) ---

def inicio(request):
    medicamentos = Medicamento.objects.all()  # Buscamos todos los medicamentos
    return render(request, 'farmaciaapp/inicio.html', {
        'medicamentos': medicamentos  # Los pasamos al HTML
    })


def login_pagina(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        usuario = authenticate(request, username=username, password=password)
        
        if usuario is not None:
            login(request, usuario)  # Crea la sesión web
            return redirect('inicio')  # Te manda a la vista principal
        else:
            return render(request, 'farmaciaapp/login.html', {
                'error': 'Usuario o contraseña incorrectos'
            })
            
    return render(request, 'farmaciaapp/login.html')


def crear_medicamento(request):
    if request.method == 'POST':
        # Usamos .get() para evitar que falle si algún campo no viene en el formulario HTML
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio', 0)
        stock = request.POST.get('stock', 0)
        categoria = request.POST.get('categoria', '')
        requiere_receta = 'requiere_receta' in request.POST  # Por si usas un checkbox

        Medicamento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria,
            requiere_receta=requiere_receta
        )
        return redirect('inicio')
        
    return render(request, 'farmaciaapp/crear.html')


def detalle_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)
    return render(request, 'farmaciaapp/detalle.html', {
        'medicamento': medicamento
    })


def editar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)

    if request.method == 'POST':
        medicamento.nombre = request.POST.get('nombre', medicamento.nombre)
        medicamento.descripcion = request.POST.get('descripcion', medicamento.descripcion)
        medicamento.precio = request.POST.get('precio', medicamento.precio)
        medicamento.stock = request.POST.get('stock', medicamento.stock)
        medicamento.categoria = request.POST.get('categoria', '')
        medicamento.requiere_receta = 'requiere_receta' in request.POST
        
        medicamento.save()
        return redirect('inicio')
    
    return render(request, 'farmaciaapp/editar.html', {
        'medicamento': medicamento
    })


def eliminar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)

    if request.method == 'POST':
        medicamento.delete()
        return redirect('inicio')
    
    return render(request, 'farmaciaapp/eliminar.html', {
        'medicamento': medicamento
    })


# --- APIS REST (CON TOKEN Y SIN SERIALIZERS) ---

class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        usuario = authenticate(
            username=username,
            password=password
        )

        if usuario is not None:
            token, creado = Token.objects.get_or_create(
                user=usuario
            )
            return Response({
                'mensaje': 'Autenticacion correcta',
                'usuario': usuario.username,
                'token': token.key
            }, status=status.HTTP_200_OK)
            
        return Response({
            'error': 'Usuario o contraseña incorrecta'
        }, status=status.HTTP_401_UNAUTHORIZED)


class MedicamentosApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        medicamentos = Medicamento.objects.all()
        datos = []

        for med in medicamentos:
            datos.append({
                'id': med.id,
                'nombre': med.nombre,
                'descripcion': med.descripcion,
                'precio': str(med.precio),
                'stock': med.stock,
                'categoria': med.categoria
            })

        return Response(datos, status=status.HTTP_200_OK)

    def post(self, request):
        nombre = request.data.get('nombre')
        descripcion = request.data.get('descripcion')
        precio = request.data.get('precio')
        stock = request.data.get('stock')
        categoria = request.data.get('categoria')

        if not nombre or not precio or not stock:
            return Response({
                'error': 'El nombre, precio y stock son obligatorios.'
            }, status=status.HTTP_400_BAD_REQUEST)

        medicamento = Medicamento.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            categoria=categoria
        )

        return Response({
            'mensaje': 'Medicamento creado correctamente',
            'medicamento': {
                'id': medicamento.id,
                'nombre': medicamento.nombre,
                'descripcion': medicamento.descripcion,
                'precio': str(medicamento.precio),
                'stock': medicamento.stock,
                'categoria': medicamento.categoria
            }
        }, status=status.HTTP_201_CREATED)


class MedicamentoDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        medicamento = get_object_or_404(Medicamento, id=id)

        return Response({
            'id': medicamento.id,
            'nombre': medicamento.nombre,
            'descripcion': medicamento.descripcion,
            'precio': str(medicamento.precio),
            'stock': medicamento.stock,
            'categoria': medicamento.categoria
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        medicamento = get_object_or_404(Medicamento, id=id)
        medicamento.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)