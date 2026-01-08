from fastapi import FastAPI
import requests, base64

app = FastAPI()

CLIENT_ID = "AYbd8q284CJWiSdJoFqYchH1dwR9-nBquQgzJVONGphZYTf_UzVuz4yZg9uKlinDaeouuDlPGL4X3lkL"
SECRET = "EHyK3lf7YPH1cpqpYoT4qBS1IHvAl-eGDcHwx7XuhElhpHi_TmG1HgAM_DHiHVNpGQ0VjmpL20gkwpyO"

def get_access_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )

    print("PAYPAL TOKEN RESPONSE:", r.status_code, r.text)

    
    return r.json()["access_token"]

@app.post("/create-order")
def create_order(total: float):
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
                "value": f"{total:.2f}"
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
    print("ORDER STATUS:", order_data.get("status"))


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








