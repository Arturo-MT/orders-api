import requests

from authentication.models import AccountSettings
from orders.models import Order
from django.contrib import messages
from django.shortcuts import redirect


def print_ticket(order_id, request):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Orden no encontrada.")
        return redirect("home")

    order_types = {
        "T": "Para llevar",
        "F": "Para comer aquí",
    }

    order_items = order.orderitem_set.all()
    total = sum(item.price for item in order_items)

    settings = AccountSettings.objects.get(user=request.user)

    addr = settings.addr

    url = f"http://{addr}:8000/imprimir"
    headers = {'Content-Type': 'application/json'}
    data = {
        "operaciones": [
            {"nombre": "Iniciar", "argumentos": []},
            # Alineación al centro
            {"nombre": "EstablecerAlineacion", "argumentos": [0]},
            {"nombre": "EstablecerTamañoFuente", "argumentos": [1, 1]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"Numero de orden: {order.order_number}\n"]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"Cliente: {order.customer_name}\n"]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"{order_types[order.type]}\n"]},
            {"nombre": "EstablecerAlineacion", "argumentos": [0]},
            {"nombre": "EscribirTexto", "argumentos": ["-" * 32 + "\n"]}
        ],
        "impresora": "86:67:7A:02:AD:A6",
        "serial": ""
    }

    for item in order_items:
        quantity = item.quantity
        name = item.product.name
        total_price = item.price

        # Formatear la línea con la cantidad y el nombre
        line = f"{quantity:<5}{name:<20}"
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": [line]
        })

        # Alineación a la derecha para los precios
        data["operaciones"].append(
            {"nombre": "EstablecerAlineacion", "argumentos": [2]})
        price_line = f"{total_price}\n"
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": [price_line]
        })

        # Resetear la alineación a la izquierda para las descripciones
        data["operaciones"].append(
            {"nombre": "EstablecerAlineacion", "argumentos": [0]})
        if item.description:
            data["operaciones"].append({
                "nombre": "EscribirTexto",
                "argumentos": [f"- {item.description}\n"]
            })
        # Agregar líneas de separación después de cada ítem
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": ["-" * 32 + "\n"]
        })

    data["operaciones"].append(
        {"nombre": "EstablecerAlineacion", "argumentos": [2]})
    data["operaciones"].append({
        "nombre": "EscribirTexto",
        "argumentos": [f"Total: {total}\n"]
    })
    data["operaciones"].append({"nombre": "Feed", "argumentos": [2]})
    data["operaciones"].append({"nombre": "Corte", "argumentos": [1]})
    data["operaciones"].append(
        {"nombre": "Pulso", "argumentos": [48, 60, 120]})

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            messages.success(
                request, "El ticket de la orden se imprimió correctamente.")
        else:
            messages.error(request, f"Error al imprimir el ticket: {
                           response.text}")
    except requests.ConnectionError:
        messages.error(
            request, "No se pudo conectar al servicio de impresión.")

    return redirect("home")
