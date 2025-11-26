from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
import cairosvg
import io
import base64

app = Flask(__name__)

def generate_time_image():
    # Strefa czasowa UTC+1
    timezone_offset = timezone(timedelta(hours=1))
    current_time_utc1 = datetime.now(timezone_offset)
    
    current_time = current_time_utc1.strftime("%H:%M:%S")
    current_date = current_time_utc1.strftime("%Y-%m-%d")
    
    # Zakoduj tło jako base64
    background_path = os.path.join('static', 'background.jpg')
    if os.path.exists(background_path):
        with open(background_path, 'rb') as f:
            background_data = base64.b64encode(f.read()).decode('utf-8')
        background_url = f"data:image/jpeg;base64,{background_data}"
    else:
        # Fallback jeśli tło nie istnieje
        background_url = ""
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Tło -->
    <defs>
        <filter id="shadow" x="0" y="0" width="200%" height="200%">
            <feOffset result="offOut" in="SourceAlpha" dx="3" dy="3" />
            <feGaussianBlur result="blurOut" in="offOut" stdDeviation="5" />
            <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
        </filter>
    </defs>
    
    <!-- Obrazek tła -->
    <image href="{background_url}" width="880" height="400"/>
    
    <!-- Czas -->
    <text x="780" y="350" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="end" font-weight="bold" filter="url(#shadow)">
        {current_time}
    </text>
    
    <!-- Data -->
    <text x="780" y="380" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="end" filter="url(#shadow)">
        {current_date}
    </text>
    
    <!-- Strefa czasowa -->
    <text x="780" y="400" font-family="Arial, sans-serif" font-size="18" fill="white" text-anchor="end" filter="url(#shadow)">
        UTC+1
    </text>
</svg>'''
    
    # Konwersja SVG do PNG
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    return png_data

@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Obrazek z godziną</title>
            <meta http-equiv="refresh" content="1">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    max-width: 900px;
                    margin: 0 auto;
                    text-align: center;
                }
                img { 
                    border: 3px solid white; 
                    border-radius: 10px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    margin: 20px 0; 
                }
                h1 {
                    font-size: 2.5em;
                    margin-bottom: 20px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }
                p {
                    font-size: 1.2em;
                    margin: 10px 0;
                }
                a {
                    color: #ffeb3b;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🕐 Aktualny czas (UTC+1)</h1>
                <img src="/time.png" alt="Aktualna godzina" width="880" height="400">
                <p>Obrazek automatycznie się odświeża co sekundę</p>
                <p>Strefa czasowa: UTC+1 (Polska, Europa Środkowa)</p>
                <p>Bezpośredni link do obrazka: <a href="/time.png">/time.png</a></p>
            </div>
        </body>
    </html>
    '''

@app.route('/time.png')
def get_time_image():
    png_data = generate_time_image()
    response = Response(png_data, mimetype='image/png')
    # Zapobieganie cache'owaniu
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)