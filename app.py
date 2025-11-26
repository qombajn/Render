from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
import cairosvg
import io

app = Flask(__name__)

def generate_time_image():
    # Strefa czasowa UTC+1
    timezone_offset = timezone(timedelta(hours=1))
    current_time_utc1 = datetime.now(timezone_offset)
    
    current_time = current_time_utc1.strftime("%H:%M:%S")
    current_date = current_time_utc1.strftime("%Y-%m-%d")
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Tło -->
    <rect width="100%" height="100%" fill="#1e3a8a"/>
    
    <!-- Gradient dla lepszego wyglądu -->
    <defs>
        <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1e3a8a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGradient)"/>
    
    <!-- Czas -->
    <text x="440" y="180" font-family="Arial, sans-serif" font-size="72" fill="white" text-anchor="middle" font-weight="bold">
        {current_time}
    </text>
    
    <!-- Data -->
    <text x="440" y="250" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="middle">
        {current_date}
    </text>
    
    <!-- Strefa czasowa -->
    <text x="440" y="300" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="middle">
        UTC+1 (Polska)
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