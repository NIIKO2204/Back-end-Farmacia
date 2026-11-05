from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required  # <-- IMPORTANTE: Para proteger las vistas web

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


@login_required(login_url='login_pagina')  # <-- Protegido: Exige login
def crear_medicamento(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion', '')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria = request.POST.get('categoria', '')
        requiere_receta = 'requiere_receta' in request.POST

        if not nombre or not precio or not stock or float(precio) <= 0:
            return render(request, 'farmaciaapp/crear.html', {
                'error': 'Todos los campos obligatorios deben estar llenos y el precio debe ser mayor a 0.'
            })

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


@login_required(login_url='login_pagina')  # <-- Protegido: Exige login
def editar_medicamento(request, id):
    medicamento = get_object_or_404(Medicamento, id=id)

    if request.method == 'POST':
        nuevo_nombre = request.POST.get('nombre')
        nueva_descripcion = request.POST.get('descripcion')
        nuevo_precio = request.POST.get('precio')
        nuevo_stock = request.POST.get('stock')
        nueva_categoria = request.POST.get('categoria')

        # Si mandan un precio y es menor o igual a 0, mostramos error
        if nuevo_precio and float(nuevo_precio) <= 0:
            return render(request, 'farmaciaapp/editar.html', {
                'medicamento': medicamento,
                'error': 'El precio no puede ser 0 o menor a 0.'
            })

        if nuevo_nombre:
            medicamento.nombre = nuevo_nombre
        if nueva_descripcion is not None:
            medicamento.descripcion = nueva_descripcion
        if nuevo_precio != '' and nuevo_precio is not None:
            medicamento.precio = nuevo_precio
        if nuevo_stock != '' and nuevo_stock is not None:
            medicamento.stock = nuevo_stock
        if nueva_categoria is not None:
            medicamento.categoria = nueva_categoria

        medicamento.requiere_receta = 'requiere_receta' in request.POST
        medicamento.save()
        return redirect('inicio')
    
    return render(request, 'farmaciaapp/editar.html', {
        'medicamento': medicamento
    })


@login_required(login_url='login_pagina')  # <-- Protegido: Exige login
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

        if not nombre or precio is None or precio == '' or float(precio) <= 0 or stock is None or stock == '':
            return Response({
                'error': 'El precio debe ser mayor a 0 y los campos obligatorios deben estar llenos.'
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

    def put(self, request, id):
        medicamento = get_object_or_404(Medicamento, id=id)

        nombre = request.data.get('nombre')
        precio = request.data.get('precio')
        stock = request.data.get('stock')

        if not nombre or precio is None or stock is None:
            return Response({
                'error': 'Para el método PUT se requieren obligatoriamente nombre, precio y stock.'
            }, status=status.HTTP_400_BAD_REQUEST)

        medicamento.nombre = nombre
        medicamento.descripcion = request.data.get('descripcion', '')
        medicamento.precio = precio
        medicamento.stock = stock
        medicamento.categoria = request.data.get('categoria', '')
        
        medicamento.save()

        return Response({
            'mensaje': 'Medicamento actualizado completamente (PUT)',
            'medicamento': {
                'id': medicamento.id,
                'nombre': medicamento.nombre,
                'descripcion': medicamento.descripcion,
                'precio': str(medicamento.precio),
                'stock': medicamento.stock,
                'categoria': medicamento.categoria
            }
        }, status=status.HTTP_200_OK)

    def patch(self, request, id):
        medicamento = get_object_or_404(Medicamento, id=id)

        if 'nombre' in request.data:
            medicamento.nombre = request.data.get('nombre')
        if 'descripcion' in request.data:
            medicamento.descripcion = request.data.get('descripcion')
        if 'precio' in request.data:
            medicamento.precio = request.data.get('precio')
        if 'stock' in request.data:
            medicamento.stock = request.data.get('stock')
        if 'categoria' in request.data:
            medicamento.categoria = request.data.get('categoria')

        medicamento.save()

        return Response({
            'mensaje': 'Medicamento actualizado parcialmente (PATCH)',
            'medicamento': {
                'id': medicamento.id,
                'nombre': medicamento.nombre,
                'descripcion': medicamento.descripcion,
                'precio': str(medicamento.precio),
                'stock': medicamento.stock,
                'categoria': medicamento.categoria
            }
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        medicamento = get_object_or_404(Medicamento, id=id)
        medicamento.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)