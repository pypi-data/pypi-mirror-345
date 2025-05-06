import requests


def send_whatsapp_template():
    url = "https://graph.facebook.com/v21.0/457380697469753/messages"

    headers = {
        "Authorization": "Bearer EAAPiZCeZCcf3QBO6M0yVfHrpvVOLyQfVGOthiPJPpgukAAxJGodp0FgTPJ8jlLte2KUXraeCbkLbFSSj0iSs7Hq6pm2fZAx3kLj8aNILBgQHBc07gLRrYRt9gHEgIbTYaMZBQa0WO3AvIhP3vB6izOjkMCpt7vhQhrtreryh4B8RpHSQbc05XAZB16CcknLTSrDMNuC8s4iTeRLoij4vTIjhCQ2IHtZA72TFQZD",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": "393533680988",
        "type": "template",
        "template": {
            "name": "invito",
            "language": {"code": "it"},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": "Lisa"}],
                }
            ],
        },
    }

    response = requests.post(url, headers=headers, json=payload)
    return response


# Example usage
if __name__ == "__main__":
    response = send_whatsapp_template()
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
