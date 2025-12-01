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
    
    # Czas cyfrowy
    current_time = current_time_utc1.strftime("%H:%M:%S")
    current_date = current_time_utc1.strftime("%Y-%m-%d")
    
    # Wartości dla zegara analogowego
    hours = current_time_utc1.hour % 12
    minutes = current_time_utc1.minute
    seconds = current_time_utc1.second
    
    # Obliczanie kątów dla wskazówek (w stopniach, zaczynając od godziny 12)
    hour_angle = (hours * 30) + (minutes * 0.5)
    minute_angle = (minutes * 6) + (seconds * 0.1)
    second_angle = seconds * 6
    
    # Współrzędne środka zegara i promień
    clock_center_x = 250
    clock_center_y = 320
    clock_radius = 80
    
    # Obliczanie współrzędnych końcowych wskazówek
    def polar_to_cartesian(angle_deg, length):
        angle_rad = math.radians(angle_deg - 90)
        x = clock_center_x + length * math.cos(angle_rad)
        y = clock_center_y + length * math.sin(angle_rad)
        return x, y
    
    # Współrzędne dla wskazówek
    hour_x, hour_y = polar_to_cartesian(hour_angle, clock_radius * 0.5)
    minute_x, minute_y = polar_to_cartesian(minute_angle, clock_radius * 0.7)
    second_x, second_y = polar_to_cartesian(second_angle, clock_radius * 0.8)
    
    # Tło - nowy kolor #58294D
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

    # Stałe pozycje dla prawidłowego wyrównania
    RIGHT_ALIGN_X = 850
    TIME_Y = 345
    DATE_Y = 390
    
    # Generowanie znaczników godzin
    hour_marks = []
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = clock_center_x + (clock_radius - 10) * math.cos(angle)
        y1 = clock_center_y + (clock_radius - 10) * math.sin(angle)
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
    
    <!-- Tło - nowy kolor #58294D -->
    <rect width="880" height="400" fill="#58294D"/>
    
    <!-- Obrazek tła (jeśli istnieje) -->
    {f'<image href="{background_url}" width="880" height="400"/>' if has_background else ""}
    
    <!-- Zegar analogowy (po lewej stronie) -->
    <!-- Okrąg tarczy zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="{clock_radius}" 
            fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="3" filter="url(#shadow)"/>
    
    <!-- Środek zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="5" fill="white"/>
    
    <!-- Znaczniki godzin -->
    <g stroke="white" stroke-width="2">
        {hour_marks_svg}
    </g>
    
    <!-- Wskazówka godzinowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{hour_x}" y2="{hour_y}" 
          stroke="white" stroke-width="6" stroke-linecap="round" filter="url(#shadow)"/>
    
    <!-- Wskazówka minutowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{minute_x}" y2="{minute_y}" 
          stroke="white" stroke-width="4" stroke-linecap="round" filter="url(#shadow)"/>
    
    <!-- Wskazówka sekundowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{second_x}" y2="{second_y}" 
          stroke="#ffcc00" stroke-width="2" stroke-linecap="round"/>
    
    <!-- Czas cyfrowy (duży, wyrównany do prawej) -->
    <text x="{RIGHT_ALIGN_X}" y="{TIME_Y}" font-family="Verdana, sans-serif" font-size="72" 
          fill="white" text-anchor="end" font-weight="bold" filter="url(#shadow)">
        {current_time}
    </text>
    
    <!-- Data (wyrównana do prawej, pod godziną) -->
    <text x="{RIGHT_ALIGN_X}" y="{DATE_Y}" font-family="Verdana, sans-serif" font-size="36" 
          fill="white" text-anchor="end" filter="url(#shadow)">
        {current_date}
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
            <title>Obrazek z zegarem analogowym i cyfrowym</title>
            <meta http-equiv="refresh" content="1">
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background: linear-gradient(135deg, #58294D 0%, #3a1a33 100%);
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
                .description {
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    margin: 20px 0;
                    text-align: left;
                }
                .features {
                    display: flex;
                    justify-content: space-around;
                    flex-wrap: wrap;
                    margin: 20px 0;
                }
                .feature {
                    background: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px;
                    flex: 1;
                    min-width: 200px;
                }
                a {
                    color: #ffcc00;
                    text-decoration: none;
                    font-weight: bold;
                }
                a:hover {
                    text-decoration: underline;
                }
                .color-box {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    background: #58294D;
                    border: 1px solid white;
                    vertical-align: middle;
                    margin: 0 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⏰ Dynamiczny Zegar Analogowy i Cyfrowy (UTC+1)</h1>
                <img src="/time.png" alt="Aktualna godzina" width="880" height="400">
                
                <div class="description">
                    <h2>Opis funkcjonalności:</h2>
                    <div class="features">
                        <div class="feature">
                            <h3>🕐 Zegar Analogowy</h3>
                            <p>Po lewej stronie - pokazuje aktualny czas za pomocą trzech wskazówek:</p>
                            <ul>
                                <li>Biała (gruba) - godziny</li>
                                <li>Biała (średnia) - minuty</li>
                                <li>Żółta (cienka) - sekundy</li>
                            </ul>
                        </div>
                        <div class="feature">
                            <h3>🎨 Nowe Tło</h3>
                            <p>Domyślne tło: <span class="color-box"></span> <strong>#58294D</strong></p>
                            <p>Można dodać własne tło umieszczając plik <code>background.jpg</code> w folderze <code>static/</code></p>
                        </div>
                        <div class="feature">
                            <h3>⚡ Dynamiczny</h3>
                            <p>Obrazek odświeża się co sekundę</p>
                            <p>Wskazówki poruszają się płynnie</p>
                            <p>Strefa czasowa: UTC+1</p>
                        </div>
                    </div>
                </div>
                
                <p>Bezpośredni link do obrazka: <a href="/time.png">/time.png</a></p>
                <p>Obrazek generowany na żądanie • Odświeżanie co 1 sekundę</p>
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