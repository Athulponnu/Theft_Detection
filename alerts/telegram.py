# telegram.py � part of alerts
# alerts/telegram.py
import requests

BOT_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# def send_telegram_alert(img_path, caption="Alert!"):
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
#     with open(img_path, "rb") as f:
#         files = {"photo": f}
#         data = {"chat_id": CHAT_ID, "caption": caption}
#         requests.post(url, files=files, data=data)

def send_telegram_alert(img_path, caption="Alert!"):
    print(f"[DUMMY TELEGRAM] 📨 Would send alert with image: {img_path}, caption: '{caption}'")
