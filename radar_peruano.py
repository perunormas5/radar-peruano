import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PERUANO = "https://diariooficial.elperuano.pe/normas"

def obtener_normas():
    try:
        response = requests.get(URL_PERUANO, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Buscamos los títulos de las normas (ajustado a la estructura común del diario)
        items = soup.find_all('h4', class_='title') 
        normas = [item.text.strip() for item in items[:10]]
        return normas
    except Exception as e:
        print(f"Error al scrapear: {e}")
        return []

def ejecutar_radar():
    normas_hoy = obtener_normas()
    if not normas_hoy:
        return

    # Memoria: leemos la última norma avisada
    archivo_db = "ultima_norma.txt"
    ultima_norma_guardada = ""
    if os.path.exists(archivo_db):
        with open(archivo_db, "r", encoding="utf-8") as f:
            ultima_norma_guardada = f.read().strip()

    # Si la más reciente es distinta a la guardada, hay novedades
    nueva_norma = normas_hoy[0]
    if nueva_norma != ultima_norma_guardada:
        mensaje = "🔔 *NUEVAS NORMAS ENCONTRADAS:*\n\n"
        for i, n in enumerate(normas_hoy[:5], 1): # Enviamos las 5 primeras
            mensaje += f"{i}. {n}\n"
        mensaje += f"\n🔗 [Ver en El Peruano]({URL_PERUANO})"
        
        # Enviar a Telegram
        url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url_tg, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
        
        # Actualizar memoria
        with open(archivo_db, "w", encoding="utf-8") as f:
            f.write(nueva_norma)

if __name__ == "__main__":
    ejecutar_radar()
