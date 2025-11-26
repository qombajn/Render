from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
from PIL import Image, ImageDraw, ImageFont
import io

app = Flask(__name__)

def generate_time_image():
    # Strefa czasowa UTC+1
    timezone_offset = timezone(timedelta(hours=1))
    current_time_utc1 = datetime.now(timezone_offset)
    
    current_time = current_time_utc1.strftime("%H:%M:%S")
    current_date = current_time_utc1.strftime("%Y-%m-%d")
    
    # Tworzenie obrazka 880x400
    img = Image.new('RGB', (880, 400), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Próba załadowania czcionki (dostosuj ścieżkę jeśli potrzeba)
    try:
        time_font = ImageFont.truetype("arial.ttf", 36)
        date_font = ImageFont.truetype("arial.ttf", 24)
    except:
        # Fallback do domyślnej czcionki
        time_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
    
    # Rysowanie czasu i daty
    draw.text((780, 320), current_time, fill='black', font=time_font, anchor="rm")
    draw.text((780, 360), current_date, fill='black', font=date_font, anchor="rm")
    
    # Dodanie informacji o strefie czasowej
    draw.text((780, 390), "UTC+1", fill='black', font=date_font, anchor="rm")
    
    # Konwersja do bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    
    return img_byte_arr.getvalue()

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Obrazek z godziną</title>
            <meta http-equiv="refresh" content="1">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                img { border: 1px solid #ccc; padding: 10px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <h1>🕐 Obrazek z aktualną godziną (UTC+1)</h1>
            <img src="/time.jpg" alt="Aktualna godzina" width="880" height="400">
            <p>Obrazek automatycznie się odświeża co sekundę</p>
            <p>Strefa czasowa: UTC+1 (Polska, Europa Środkowa)</p>
            <p>Bezpośredni link do obrazka: <a href="/time.jpg">/time.jpg</a></p>
        </body>
    </html>
    '''

@app.route('/time.jpg')
def get_time_image():
    jpg_data = generate_time_image()
    response = Response(jpg_data, mimetype='image/jpeg')
    # Zapobieganie cache'owaniu
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)