#!/usr/bin/env python3
"""
Nexus Games & Apps Hub Telegram Bot (@my_games_hub_bot)
Ultra-lightweight serverless bot daemon using Python 3 stdlib.
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import time

HUB_URL = "https://goanscryca.github.io/ton-survivors/hub.html"
MARIO_URL = "https://goanscryca.github.io/ton-survivors/mario.html"
BATTLER_URL = "https://goanscryca.github.io/ton-survivors/battler.html"
TYCOON_URL = "https://goanscryca.github.io/ton-survivors/tycoon.html"
SURVIVORS_URL = "https://goanscryca.github.io/ton-survivors/"

def api_call(token: str, method: str, data: dict | None = None) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"API Error ({method}): {e}", file=sys.stderr)
        return {"ok": False, "error": str(e)}

def setup_bot(token: str):
    # 1. Set Menu Button
    api_call(token, "setChatMenuButton", {
        "menu_button": {
            "type": "web_app",
            "text": "🌌 NEXUS HUB",
            "web_app": {"url": HUB_URL}
        }
    })
    # 2. Set Commands
    api_call(token, "setMyCommands", {
        "commands": [
            {"command": "start", "description": "Открыть Nexus Hub и каталог"},
            {"command": "hub", "description": "Запустить Web3 Games & Apps Hub"},
            {"command": "games", "description": "Список доступных игр"}
        ]
    })
    # 3. Set Description
    api_call(token, "setMyDescription", {
        "description": "Nexus Hub — единый центр Web3-игр, приложений и маркетплейса в Telegram. Играй, прокачивай профиль и привязывай кошельки!"
    })

def send_welcome(token: str, chat_id: int, first_name: str):
    text = (
        f"Добро пожаловать в **Nexus Hub**, {first_name}! 🌌\n\n"
        "🏛️ **Единый центр Web3-игр, приложений и маркетплейса:**\n\n"
        "• 🍄 **Super Mario: World 1-1** — первый уровень легендарного платформера с монетами, грибами и Гумбами!\n"
        "• Единый профиль: аватарка, никнейм, статус и привязка кошелька\n"
        "• Магазин: Web3-платежи и донаты на личные кошельки\n\n"
        "Нажми **«ОТКРЫТЬ NEXUS HUB»** или запускай Марио прямо сейчас 👇"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🌌 ОТКРЫТЬ NEXUS HUB 🚀", "web_app": {"url": HUB_URL}}
            ],
            [
                {"text": "🍄 Играть в Super Mario 1-1", "web_app": {"url": MARIO_URL}}
            ]
        ]
    }
    api_call(token, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": keyboard
    })

def main():
    token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("HUB_BOT_TOKEN")
    if not token:
        print("Error: HUB_BOT_TOKEN is required", file=sys.stderr)
        sys.exit(1)

    print("Configuring @my_games_hub_bot...")
    setup_bot(token)
    print("Bot configured successfully! Starting long polling...")

    offset = 0
    while True:
        try:
            res = api_call(token, "getUpdates", {
                "offset": offset,
                "timeout": 20,
                "allowed_updates": ["message"]
            })
            if res.get("ok"):
                for update in res.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message")
                    if not msg:
                        continue
                    chat_id = msg["chat"]["id"]
                    first_name = msg.get("from", {}).get("first_name", "Пилот")
                    text = msg.get("text", "")

                    if text.startswith("/start") or text.startswith("/hub"):
                        send_welcome(token, chat_id, first_name)
                    elif text.startswith("/games"):
                        send_welcome(token, chat_id, first_name)
        except Exception as e:
            print(f"Polling loop error: {e}", file=sys.stderr)
            time.sleep(3)

if __name__ == "__main__":
    main()
