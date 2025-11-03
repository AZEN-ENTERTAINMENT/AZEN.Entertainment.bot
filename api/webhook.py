# api/webhook.py
import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")  # توکن ربات
SECRET = os.environ.get("WORKER_SHARED_SECRET", "my-secret-123")  # secret مشترک

def telegram_send(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("x-worker-secret", "") != SECRET:
        return jsonify({"status": "forbidden"}), 403

    update = request.get_json()
    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]
        telegram_send(chat_id, f"پیام دریافت شد: {text}")

    return jsonify({"status": "ok"})
