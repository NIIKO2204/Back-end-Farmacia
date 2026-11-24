import requests

URL = "http://127.0.0.1:8000"

datos = {"username": "eric", "password": "1234"}

# 1. Obtener los tokens
respuesta = requests.post(f"{URL}/api/token/", json=datos)

if respuesta.status_code == 200:

    tokens = respuesta.json()
    access = tokens["access"]
    refresh = tokens["refresh"]

    print("Autenticación exitosa")

    # 2. Utilizar Access Token para consultar medicamentos
    headers = {"Authorization": f"Bearer {access}"}

    respuesta_medicamentos = requests.get(
        f"{URL}/api/medicamentos/", headers=headers
    )

    print("\nCódigo HTTP:", respuesta_medicamentos.status_code)

    if respuesta_medicamentos.status_code == 200:
        print("Medicamentos registrados:")
        print(respuesta_medicamentos.json())
    else:
        print("Error:", respuesta_medicamentos.text)

else:
    print("Error al iniciar sesión:", respuesta.text)


# 3. Crear un nuevo medicamento mediante POST

nuevo_medicamento = {
    "nombre": "Paracetamol 500mg",
    "descripcion": "Analgésico y antipirético, caja de 20 comprimidos",
    "precio": 2500.00,
    "stock": 30,
    "disponible": True,
}

respuesta_creacion = requests.post(
    f"{URL}/api/medicamentos/", json=nuevo_medicamento, headers=headers
)

print("\nCreación de medicamento:")
print("Código HTTP:", respuesta_creacion.status_code)
print(respuesta_creacion.json())


# 4. Actualizar un medicamento mediante PUT

id_medicamento = 2

datos_actualizados = {
    "nombre": "Paracetamol 500mg Forte",
    "descripcion": "Probando el método PUT con JWT en farmacia",
    "precio": 3200.00,
    "stock": 45,
    "disponible": True,
}

respuesta_put = requests.put(
    f"{URL}/api/medicamentos/{id_medicamento}/",
    json=datos_actualizados,
    headers=headers,
)

print("\nActualización de medicamento:")
print("Código HTTP:", respuesta_put.status_code)
print(respuesta_put.json())


# 5. Eliminar un medicamento mediante DELETE

id_medicamento = 3

respuesta_delete = requests.delete(
    f"{URL}/api/medicamentos/{id_medicamento}/", headers=headers
)

print("\nEliminación de medicamento:")
print("Código HTTP:", respuesta_delete.status_code)

if respuesta_delete.status_code == 204:
    print("Medicamento eliminado correctamente")
else:
    print(respuesta_delete.text)


# 6. Renovar Access Token utilizando Refresh Token

respuesta_refresh = requests.post(
    f"{URL}/api/token/refresh/", json={"refresh": refresh}
)

print("\nRenovación de Access Token:")
print("Código HTTP:", respuesta_refresh.status_code)

if respuesta_refresh.status_code == 200:

    nuevos_tokens = respuesta_refresh.json()

    access = nuevos_tokens["access"]
    refresh = nuevos_tokens.get("refresh", refresh)

    print("Access Token renovado correctamente")
    print("Nuevo Refresh Token recibido:", "refresh" in nuevos_tokens)

else:
    print("Error al renovar:", respuesta_refresh.text)