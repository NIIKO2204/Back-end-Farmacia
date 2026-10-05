from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Medicamento

# Create your views here.

# def inicio(request):
#     return HttpResponse("Hola, esta es mi App de Farmacia")

def inicio(request):
    medicamentos = Medicamento.objects.all()

    return render(request, 'farmaciaapp/inicio.html', {
        'medicamentos': medicamentos
    }) 

def crear_medicamento(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        requiere_receta = 'requiere_receta' in request.POST

        Medicamento.objects.create(
            nombre = nombre,
            descripcion = descripcion,
            precio = precio,
            stock = stock,
            requiere_receta = requiere_receta
        )
        return redirect('inicio')

    return render(request, 'farmaciaapp/crear.html')


def detalle_medicamento(request, id):
    medicamento = Medicamento.objects.get(id=id)

    return render(request, 'farmaciaapp/detalle.html', {
        'medicamento': medicamento
    })

def editar_medicamento(request, id):
    medicamento = Medicamento.objects.get(id=id)

    if request.method == 'POST':
        medicamento.nombre = request.POST['nombre']
        medicamento.descripcion = request.POST['descripcion']
        medicamento.precio = request.POST['precio']
        medicamento.stock = request.POST['stock']
        medicamento.requiere_receta = 'requiere_receta' in request.POST

        medicamento.save()
        return redirect('inicio')
        
    return render(request, 'farmaciaapp/editar.html', {
        'medicamento': medicamento
    })

def eliminar_medicamento(request, id):
    medicamento = Medicamento.objects.get(id=id)

    if request.method == 'POST':
        medicamento.delete()
        return redirect('inicio')

    return render(request, 'farmaciaapp/eliminar.html', {
        'medicamento': medicamento
    })