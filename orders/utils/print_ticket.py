import requests
from orders.models import Order


def print_ticket(order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return 404, "Order not found"

    order_types = {
        "T": "Para llevar",
        "F": "Para comer aqui",
    }

    # Calculate the total by summing the total of each order_item
    order_items = order.orderitem_set.all()
    total = sum(item.price for item in order_items)

    url = "http://192.168.50.144:8000/imprimir"
    headers = {'Content-Type': 'application/json'}
    data = {
        "operaciones": [
            {"nombre": "Iniciar", "argumentos": []},
            {"nombre": "EstablecerAlineacion",
                "argumentos": [0]},  # Center alignment
            {"nombre": "EstablecerTamañoFuente", "argumentos": [1, 1]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"Numero de orden: {order.order_number}\n"]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"Cliente: {order.customer_name}\n"]},
            {"nombre": "EscribirTexto", "argumentos": [
                f"{order_types[order.type]}\n"]},
            # Left alignment for items
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

        # Format the line with quantity and name
        line = f"{quantity:<5}{name:<20}"
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": [line]
        })

        # Right alignment for prices
        data["operaciones"].append(
            {"nombre": "EstablecerAlineacion", "argumentos": [2]})
        price_line = f"{total_price}\n"
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": [price_line]
        })

        # Reset alignment to left for descriptions
        data["operaciones"].append(
            {"nombre": "EstablecerAlineacion", "argumentos": [0]})
        if item.description:
            data["operaciones"].append({
                "nombre": "EscribirTexto",
                "argumentos": [f"- {item.description}\n"]
            })
        # Add separation lines after each item
        data["operaciones"].append({
            "nombre": "EscribirTexto",
            "argumentos": ["-" * 32 + "\n"]
        })

    data["operaciones"].append({"nombre": "EstablecerAlineacion", "argumentos": [
                               2]})  # Center alignment for total
    data["operaciones"].append({
        "nombre": "EscribirTexto",
        "argumentos": [f"Total: {total}\n"]
    })
    data["operaciones"].append({"nombre": "Feed", "argumentos": [2]})
    data["operaciones"].append({"nombre": "Corte", "argumentos": [1]})
    data["operaciones"].append(
        {"nombre": "Pulso", "argumentos": [48, 60, 120]})

    response = requests.post(url, json=data, headers=headers)
    return response.status_code, response.text
