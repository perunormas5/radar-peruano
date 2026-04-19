import requests
from bs4 import BeautifulSoup
import os

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PERUANO = "https://diariooficial.elperuano.pe/normas"

def obtener_normas():
    try:
        # Añadimos un "User-Agent" para que la web no nos bloquee
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(URL_PERUANO, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # El Peruano suele usar la clase 'title' o 'busqueda_v_titulo'
        items = soup.find_all(['h4', 'span'], class_=['title', 'busqueda_v_titulo'])
        
        normas = [item.text.strip() for item in items if item.text.strip()]
        return normas
    except Exception as e:
        print(f"Error al scrapear: {e}")
        return []

def ejecutar_radar():
    normas_hoy = obtener_normas()
    
    # Si no encuentra nada, mandamos un aviso de error para saber qué pasa
    if not normas_hoy:
        print("No se encontraron normas en la página.")
        return

    archivo_db = "ultima_norma.txt"
    ultima_norma_guardada = ""
    if os.path.exists(archivo_db):
        with open(archivo_db, "r", encoding="utf-8") as f:
            ultima_norma_guardada = f.read().strip()

    # Si la primera norma es distinta, avisamos
    if normas_hoy[0] != ultima_norma_guardada:
        mensaje = "🔔 *RADAR EL PERUANO ACTIVADO*\n\n"
        mensaje += "Últimas normas detectadas:\n"
        for i, n in enumerate(normas_hoy[:5], 1):
            mensaje += f"{i}. {n}\n"
        mensaje += f"\n🔗 [Ver Normas]({URL_PERUANO})"
        
        url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url_tg, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
        
        if r.status_code == 200:
            with open(archivo_db, "w", encoding="utf-8") as f:
                f.write(normas_hoy[0])
        else:
            print(f"Error enviando a Telegram: {r.text}")

if __name__ == "__main__":
    ejecutar_radar()
