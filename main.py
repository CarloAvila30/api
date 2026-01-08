from fastapi import FastAPI
import requests, base64

app = FastAPI()

CLIENT_ID = "AXxQmiGf-wH4T6wHdaG8iQ6HCajwKnnkl_RDrptk3DQJSKJEHT3QHOXBlJW-4xFMOUp6XMCoLeeLhuXa"
SECRET = "EHxMVI7-7HQpgb5s24KL-4F20ScD4hWwmy1_Uxfu7YW3UptAJzg1xJqLYp7MLvCL1Tmly7fxs6sh81Jf"

def get_access_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]

@app.post("/create-order")
def create_order():
    access_token = get_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "MXN",
                "value": "50.00"
            }
        }],
        "application_context": {
            "return_url": "icehelados://paypal/success",
            "cancel_url": "icehelados://paypal/cancel"
        }
    }

    response = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        json=body,
        headers=headers
    )

    return response.json()


@app.post("/capture-order/{order_id}")
def capture_order(order_id: str):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1️⃣ CONSULTAR EL ESTADO DE LA ORDEN
    check = requests.get(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}",
        headers=headers
    )

    order_data = check.json()

    # 🔒 SI NO ESTÁ APROBADA, NO CAPTURAR
    if order_data.get("status") != "APPROVED":
        return {
            "error": "Order not approved",
            "status": order_data.get("status")
        }

    # 2️⃣ CAPTURAR SOLO SI ESTÁ APPROVED
    capture = requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
        headers=headers
    )

    return capture.json()


