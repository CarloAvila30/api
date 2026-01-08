from fastapi import FastAPI
import requests, base64

app = FastAPI()

CLIENT_ID = "AXxQmiGf-wH4T6wHdaG8iQ6HCajwKnnkl_RDrptk3DQJSKJEHT3QHOXBlJW-4xFMOUp6XMCoLeeLhuXa"
SECRET = "EHxMVI7-7HQpgb5s24KL-4F20ScD4hWwmy1_Uxfu7YW3UptAJzg1xJqLYp7MLvCL1Tmly7fxs6sh81Jf"

def get_token():
    auth = base64.b64encode(f"{CLIENT_ID}:{SECRET}".encode()).decode()
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        headers={"Authorization": f"Basic {auth}"},
        data={"grant_type": "client_credentials"}
    )
    return r.json()["access_token"]

@app.post("/create-order")
def create_order(total: float):
    token = get_token()
    r = requests.post(
        "https://api-m.sandbox.paypal.com/v2/checkout/orders",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {
                    "currency_code": "MXN",
                    "value": f"{total:.2f}"
                }
            }],
            "application_context": {
                "return_url": "icehelados://paypal/success",
                "cancel_url": "icehelados://paypal/cancel",
                "user_action": "PAY_NOW"
            }
        }
    )
    return r.json()
