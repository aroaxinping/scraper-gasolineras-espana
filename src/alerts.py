import os
import requests

def send_telegram_alert(message: str):
    """Envía un mensaje a un bot de Telegram si las credenciales están configuradas."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("[Alert] No hay credenciales de Telegram configuradas.")
        print(f"[Alert Message]: {message}")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        print("Notificación de Telegram enviada.")
    except Exception as e:
        print(f"Error enviando Telegram: {e}")

def check_for_drops(current_means: dict, previous_means: dict):
    """Compara medias y envía alertas si hay bajadas significativas (>2%)."""
    if not previous_means:
        return

    for fuel in ["g95", "diesel"]:
        curr = current_means.get(fuel)
        prev = previous_means.get(fuel)
        
        if curr and prev:
            diff = curr - prev
            pct = (diff / prev) * 100
            
            # Si baja más de un 2%
            if pct <= -2.0:
                fuel_name = "Gasolina 95" if fuel == "g95" else "Diesel"
                msg = (
                    f"🚨 *¡Baja histórica de precios detectada!*\n"
                    f"El precio medio de *{fuel_name}* ha bajado un *{abs(pct):.2f}%*.\n"
                    f"De {prev:.3f} €/L a `{curr:.3f} €/L`."
                )
                send_telegram_alert(msg)
