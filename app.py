from flask import Flask, Response
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

def generate_time_image():
    # Tworzenie obrazka
    img = Image.new('RGB', (400, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    # Aktualna data i godzina
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Prosta czcionka (bez zależności od systemowych czcionek)
    try:
        # Próba załadowania domyślnej czcionki
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    except:
        # Fallback na podstawową czcionkę
        font_large = None
        font_small = None
    
    # Rysowanie tekstu
    draw.text((50, 30), f"Godzina: {current_time}", fill='black', font=font_large)
    draw.text((50, 80), f"Data: {current_date}", fill='blue', font=font_small)
    
    # Konwersja do bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

@app.route('/')
def home():
    return """
    <html>
        <head>
            <title>Obrazek z godziną</title>
            <meta http-equiv="refresh" content="1">
        </head>
        <body>
            <h1>Obrazek z aktualną godziną</h1>
            <img src="/time.png" style="border: 1px solid #ccc; margin: 20px;">
            <p>Obrazek automatycznie się odświeża co sekundę</p>
            <p>Bezpośredni link do obrazka: <a href="/time.png">/time.png</a></p>
        </body>
    </html>
    """

@app.route('/time.png')
def get_time_image():
    img_bytes = generate_time_image()
    response = Response(img_bytes.getvalue(), mimetype='image/png')
    # Zapobieganie cache'owaniu
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)