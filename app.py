from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
import cairosvg
import io
import base64
import math

app = Flask(__name__)

def generate_time_image():
    # Ustawienie strefy czasowej na UTC+1
    timezone_offset = timezone(timedelta(hours=1))
    current_time_utc1 = datetime.now(timezone_offset)
    
    # Czas cyfrowy - BEZ SEKUND
    current_time = current_time_utc1.strftime("%H:%M")
    current_date = current_time_utc1.strftime("%Y-%m-%d")
    
    # Wartości dla zegara analogowego - BEZ SEKUND
    hours = current_time_utc1.hour % 12
    minutes = current_time_utc1.minute
    
    # Obliczanie kątów dla wskazówek (w stopniach, zaczynając od godziny 12)
    hour_angle = (hours * 30) + (minutes * 0.5)  # 30 stopni na godzinę + 0.5 stopnia na minutę
    minute_angle = minutes * 6  # 6 stopni na minutę
    
    # NOWE: Współrzędne środka zegara analogowego (blisko czasu cyfrowego)
    clock_center_x = 520  # Przesunięty bliżej czasu cyfrowego
    clock_center_y = 340  # Ta sama wysokość co czas cyfrowy
    clock_radius = 48
    
    # Obliczanie współrzędnych końcowych wskazówek
    def polar_to_cartesian(angle_deg, length):
        angle_rad = math.radians(angle_deg - 90)
        x = clock_center_x + length * math.cos(angle_rad)
        y = clock_center_y + length * math.sin(angle_rad)
        return x, y
    
    # Współrzędne dla wskazówek
    hour_x, hour_y = polar_to_cartesian(hour_angle, clock_radius * 0.5)
    minute_x, minute_y = polar_to_cartesian(minute_angle, clock_radius * 0.7)
    
    # Tło - kolor #58294D
    background_path = os.path.join('static', 'background.jpg')
    background_url = ""
    has_background = False
    
    if os.path.exists(background_path):
        try:
            with open(background_path, 'rb') as f:
                background_data = base64.b64encode(f.read()).decode('utf-8')
            background_url = f"data:image/jpeg;base64,{background_data}"
            has_background = True
        except Exception:
            has_background = False

    # NOWE: Stałe pozycje dla czasu i daty (przesunięte bliżej zegara)
    TIME_X = 250  # Czas cyfrowy bardziej na lewo, bliżej zegara
    DATE_X = 250  # Data w tej samej pozycji co czas
    TIME_Y = 340  # Ta sama wysokość co zegar
    DATE_Y = 390  # Pod godziną
    
    # Generowanie znaczników godzin
    hour_marks = []
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = clock_center_x + (clock_radius - 6) * math.cos(angle)
        y1 = clock_center_y + (clock_radius - 6) * math.sin(angle)
        x2 = clock_center_x + clock_radius * math.cos(angle)
        y2 = clock_center_y + clock_radius * math.sin(angle)
        hour_marks.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    
    hour_marks_svg = ''.join(hour_marks)
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
    <defs>
        <filter id="shadow" x="0" y="0" width="200%" height="200%">
            <feOffset result="offOut" in="SourceAlpha" dx="3" dy="3" />
            <feGaussianBlur result="blurOut" in="offOut" stdDeviation="5" />
            <feBlend in="SourceGraphic" in2="blurOut" mode="normal" />
        </filter>
        <filter id="dropShadow" x="-50%" y="-50%" width="200%" height="200%">
            <feDropShadow dx="2" dy="2" stdDeviation="2" flood-color="black" flood-opacity="0.5"/>
        </filter>
    </defs>
    
    <!-- Tło - kolor #58294D -->
    <rect width="880" height="400" fill="#58294D"/>
    
    <!-- Obrazek tła (jeśli istnieje) -->
    {f'<image href="{background_url}" width="880" height="400"/>' if has_background else ""}
    
    <!-- Czas cyfrowy (blisko zegara analogowego) - BEZ SEKUND -->
    <text x="{TIME_X}" y="{TIME_Y}" font-family="Verdana, sans-serif" font-size="60" 
          fill="white" text-anchor="start" font-weight="bold" filter="url(#shadow)">
        {current_time}
    </text>
    
    <!-- Data (pod godziną, na tej samej wysokości co zegar) -->
    <text x="{DATE_X}" y="{DATE_Y}" font-family="Verdana, sans-serif" font-size="32" 
          fill="white" text-anchor="start" filter="url(#shadow)">
        {current_date}
    </text>
    
    <!-- Zegar analogowy (blisko czasu cyfrowego) -->
    <!-- Okrąg tarczy zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="{clock_radius}" 
            fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.8" filter="url(#shadow)"/>
    
    <!-- Środek zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="3" fill="white"/>
    
    <!-- Znaczniki godzin -->
    <g stroke="white" stroke-width="1.2">
        {hour_marks_svg}
    </g>
    
    <!-- Wskazówka godzinowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{hour_x}" y2="{hour_y}" 
          stroke="white" stroke-width="3.6" stroke-linecap="round" filter="url(#shadow)"/>
    
    <!-- Wskazówka minutowa - KOLOR #FFCC00 -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{minute_x}" y2="{minute_y}" 
          stroke="#FFCC00" stroke-width="2.4" stroke-linecap="round" filter="url(#shadow)"/>
</svg>'''
    
    # Konwersja SVG do PNG
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    return png_data

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
        <head>
            <title>Zegar</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body { 
                    margin: 0; 
                    padding: 10px; 
                    background: #58294D;
                    text-align: center;
                    font-family: Arial, sans-serif;
                }
                img { 
                    display: block; 
                    margin: 0 auto; 
                    max-width: 100%;
                }
                .info {
                    color: white;
                    margin-top: 10px;
                    font-size: 14px;
                }
            </style>
        </head>
        <body>
            <img src="/time.png" alt="Aktualna godzina">
            <div class="info">
                Odświeżanie co 10 sekund • UTC+1
            </div>
        </body>
    </html>
    '''

@app.route('/time.png')
def get_time_image():
    png_data = generate_time_image()
    response = Response(png_data, mimetype='image/png')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)