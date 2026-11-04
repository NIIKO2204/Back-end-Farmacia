from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Tarea

# --- VISTAS TRADICIONALES (WEB HTML) ---

def login_pagina(request):
    return render(request, 'tareasapp/login.html')

def inicio(request):
    tareas = Tarea.objects.all()
    return render(request, 'tareasapp/inicio.html', {
        'tareas': tareas
    })  

def crear_tarea(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        completada = 'completada' in request.POST

        if not titulo or not descripcion:
            return render(request, 'tareasapp/crear.html', {
                'error': 'El título y la descripción son obligatorios.'
            })

        if len(titulo) > 35 or len(descripcion) > 50:
            return render(request, 'tareasapp/crear.html', {
                'error': 'Se ha superado el límite permitido (Máx. 35 para título, 50 para descripción).'
            })

        Tarea.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            completada=completada
        )
        return redirect('inicio')
    return render(request, 'tareasapp/crear.html')

def detalle_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)
    return render(request, 'tareasapp/detalle.html', {
        'tarea': tarea
    })

def editar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        completada = 'completada' in request.POST

        if not titulo or not descripcion:
            return render(request, 'tareasapp/editar.html', {
                'tarea': tarea,
                'error': 'Los campos no pueden estar vacíos.'
            })

        if len(titulo) > 35 or len(descripcion) > 50:
            return render(request, 'tareasapp/editar.html', {
                'tarea': tarea,
                'error': 'Se ha superado el límite permitido (Máx. 35 para título, 50 para descripción).'
            })

        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.completada = completada
        tarea.save()
        return redirect('inicio')
    
    return render(request, 'tareasapp/editar.html', {
        'tarea': tarea
    })

def eliminar_tarea(request, id):
    tarea = get_object_or_404(Tarea, id=id)

    if request.method == 'POST':
        tarea.delete()
        return redirect('inicio')
    
    return render(request, 'tareasapp/eliminar.html', {
        'tarea': tarea
    })


# --- API REST (DJANGO REST FRAMEWORK) ---

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


class TareasApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tareas = Tarea.objects.all()
        datos = []

        for tarea in tareas:
            datos.append({
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'completada': tarea.completada
            })

        return Response(datos, status.HTTP_200_OK)
    
    def post(self, request):
        titulo = request.data.get('titulo', '').strip()
        descripcion = request.data.get('descripcion', '').strip()
        completada = request.data.get('completada', False)

        if not titulo or not descripcion:
            return Response({
                'error': 'El título y la descripción son obligatorios y no pueden estar vacíos.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(titulo) > 35:
            return Response({
                'error': 'El título no puede superar los 35 caracteres.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(descripcion) > 50:
            return Response({
                'error': 'La descripción no puede superar los 50 caracteres.'
            }, status=status.HTTP_400_BAD_REQUEST)

        tarea = Tarea.objects.create(
            titulo=titulo, 
            descripcion=descripcion,
            completada=completada
        )
       
        return Response({
            'mensaje': 'Tarea creada correctamente',
            'tarea': {
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'completada': tarea.completada
            }
        }, status=status.HTTP_201_CREATED)


class TareaDetalleApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        tarea = get_object_or_404(Tarea, id=id)

        return Response({
            'id': tarea.id,
            'titulo': tarea.titulo,
            'descripcion': tarea.descripcion,
            'completada': tarea.completada
        }, status=status.HTTP_200_OK)
    
    def put(self, request, id):
        tarea = get_object_or_404(Tarea, id=id)
        
        titulo = request.data.get('titulo', tarea.titulo).strip()
        descripcion = request.data.get('descripcion', tarea.descripcion).strip()
        completada = request.data.get('completada', tarea.completada)

        if not titulo or not descripcion:
            return Response({
                'error': 'Los campos no pueden quedar vacíos.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if len(titulo) > 35 or len(descripcion) > 50:
            return Response({
                'error': 'Se ha excedido el límite permitido (Máx. 35 título, 50 descripción).'
            }, status=status.HTTP_400_BAD_REQUEST)

        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.completada = completada
        tarea.save()

        return Response({
            'mensaje': 'Tarea actualizada correctamente',
            'tarea': {
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'completada': tarea.completada
            }
        }, status=status.HTTP_200_OK)

    def patch(self, request, id):
        tarea = get_object_or_404(Tarea, id=id)
        
        titulo = request.data.get('titulo', tarea.titulo)
        if isinstance(titulo, str):
            titulo = titulo.strip()
            if len(titulo) > 35:
                return Response({'error': 'El título no puede superar los 35 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
            if not titulo:
                return Response({'error': 'El título no puede estar vacío.'}, status=status.HTTP_400_BAD_REQUEST)

        descripcion = request.data.get('descripcion', tarea.descripcion)
        if isinstance(descripcion, str):
            descripcion = descripcion.strip()
            if len(descripcion) > 50:
                return Response({'error': 'La descripción no puede superar los 50 caracteres.'}, status=status.HTTP_400_BAD_REQUEST)
            if not descripcion:
                return Response({'error': 'La descripción no puede estar vacía.'}, status=status.HTTP_400_BAD_REQUEST)

        completada = request.data.get('completada', tarea.completada)

        tarea.titulo = titulo
        tarea.descripcion = descripcion
        tarea.completada = completada
        tarea.save()

        return Response({
            'mensaje': 'Tarea actualizada parcialmente correctamente',
            'tarea': {
                'id': tarea.id,
                'titulo': tarea.titulo,
                'descripcion': tarea.descripcion,
                'completada': tarea.completada
            }
        }, status=status.HTTP_200_OK)

    def delete(self, request, id):
        tarea = get_object_or_404(Tarea, id=id)
        tarea.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)