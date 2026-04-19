import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

# Configuración desde Secrets de GitHub
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PERUANO = "https://diariooficial.elperuano.pe/normas"

def es_horario_extraordinario():
    # Definimos la zona horaria de Perú
    tz_peru = pytz.timezone('America/Lima')
    hora_actual = datetime.now(tz_peru)
    # Las normas ordinarias salen a las 5-6 AM. 
    # Si detectamos algo nuevo después de las 9 AM, es extraordinaria.
    return hora_actual.hour >= 9

def obtener_normas():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(URL_PERUANO, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscamos los títulos de las normas
        items = soup.find_all(['h4', 'span'], class_=['title', 'busqueda_v_titulo'])
        normas = [item.text.strip() for item in items if item.text.strip()]
        return normas
    except Exception as e:
        print(f"Error: {e}")
        return []

def ejecutar_radar():
    normas_detectadas = obtener_normas()
    if not normas_detectadas:
        print("No se encontraron normas.")
        return

    archivo_db = "ultima_norma.txt"
    ultima_norma_guardada = ""
    
    if os.path.exists(archivo_db):
        with open(archivo_db, "r", encoding="utf-8") as f:
            ultima_norma_guardada = f.read().strip()

    nueva_norma = normas_detectadas[0]

    # LÓGICA: Solo avisa si es distinta a la guardada Y es horario de extraordinarias
    if nueva_norma != ultima_norma_guardada:
        if es_horario_extraordinario():
            mensaje = "🚨 *¡ALERTA: EDICIÓN EXTRAORDINARIA!* 🚨\n\n"
            mensaje += f"Se ha detectado una nueva publicación:\n\n* {nueva_norma}\n"
            mensaje += f"\n🔗 [Revisar en El Peruano]({URL_PERUANO})"
            
            url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url_tg, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
            print("Mensaje enviado a Telegram.")
        
        # Guardamos la nueva norma como "leída"
        with open(archivo_db, "w", encoding="utf-8") as f:
            f.write(nueva_norma)
    else:
        print("Sin cambios detectados.")

if __name__ == "__main__":
    ejecutar_radar()
