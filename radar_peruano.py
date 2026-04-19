import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_PERUANO = "https://diariooficial.elperuano.pe/normas"

def es_horario_extraordinario():
    tz_peru = pytz.timezone('America/Lima')
    hora_actual = datetime.now(tz_peru)
    return hora_actual.hour >= 9

def obtener_normas():
    # DISFRAZ DE NAVEGADOR: Esto evita que la web nos bloquee
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
    }
    try:
        response = requests.get(URL_PERUANO, headers=headers, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BUSQUEDA AGRESIVA: Buscamos títulos en diferentes etiquetas posibles
        normas = []
        
        # Intento 1: Buscar por la clase 'title' que suelen usar
        items = soup.find_all('h4', class_='title')
        
        # Intento 2: Si el 1 falló, buscar por el link de la norma
        if not items:
            items = soup.select('div.normas_listado h4')
            
        # Intento 3: Buscar cualquier enlace dentro de la sección de normas
        if not items:
            items = soup.find_all('a', href=True)
            for a in items:
                if 'normas' in a['href'] and len(a.text.strip()) > 20:
                    normas.append(a.text.strip())
        else:
            normas = [item.text.strip() for item in items if item.text.strip()]

        return normas
    except Exception as e:
        print(f"Error de conexión: {e}")
        return []

def ejecutar_radar():
    normas_detectadas = obtener_normas()
    
    if not normas_detectadas:
        print("Sigue sin encontrar normas. Intentando método alternativo...")
        return

    print(f"Normas encontradas: {len(normas_detectadas)}")
    
    archivo_db = "ultima_norma.txt"
    ultima_norma_guardada = ""
    
    if os.path.exists(archivo_db):
        with open(archivo_db, "r", encoding="utf-8") as f:
            ultima_norma_guardada = f.read().strip()

    nueva_norma = normas_detectadas[0]

    if nueva_norma != ultima_norma_guardada:
        # Solo avisar si es horario extraordinario (después de las 9am)
        if es_horario_extraordinario():
            mensaje = "🚨 *RADAR EL PERUANO: NUEVA PUBLICACIÓN* 🚨\n\n"
            mensaje += f"Se detectó un nuevo título:\n\n* {nueva_norma}\n"
            mensaje += f"\n🔗 [Ir a El Peruano]({URL_PERUANO})"
            
            url_tg = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            requests.post(url_tg, json={"chat_id": CHAT_ID, "text": mensaje, "parse_mode": "Markdown"})
        
        # Actualizar memoria para evitar spam
        with open(archivo_db, "w", encoding="utf-8") as f:
            f.write(nueva_norma)
    else:
        print("Todo igual, no hay normas nuevas.")

if __name__ == "__main__":
    ejecutar_radar()
