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
    
    # Współrzędne środka zegara analogowego (przesunięty na prawą stronę)
    clock_center_x = 680  # Przesunięty bardziej w prawo
    clock_center_y = 320
    clock_radius = 48  # 80 * 0.6 = 48 (40% mniejsze niż oryginalne 80px)
    
    # Obliczanie współrzędnych końcowych wskazówek
    def polar_to_cartesian(angle_deg, length):
        angle_rad = math.radians(angle_deg - 90)
        x = clock_center_x + length * math.cos(angle_rad)
        y = clock_center_y + length * math.sin(angle_rad)
        return x, y
    
    # Współrzędne dla wskazówek - TYLKO GODZINOWA I MINUTOWA
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

    # Stałe pozycje dla czasu i daty (teraz z lewej strony)
    LEFT_ALIGN_X = 150  # Wyrównanie do lewej
    TIME_Y = 340  # Przesunięte wyżej, bliżej daty
    DATE_Y = 390
    
    # Generowanie znaczników godzin
    hour_marks = []
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = clock_center_x + (clock_radius - 6) * math.cos(angle)  # Dostosowane do mniejszego zegara
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
    
    <!-- Czas cyfrowy (z lewej strony) - BEZ SEKUND -->
    <text x="{LEFT_ALIGN_X}" y="{TIME_Y}" font-family="Verdana, sans-serif" font-size="68" 
          fill="white" text-anchor="start" font-weight="bold" filter="url(#shadow)">
        {current_time}
    </text>
    
    <!-- Data (z lewej strony, pod godziną) -->
    <text x="{LEFT_ALIGN_X}" y="{DATE_Y}" font-family="Verdana, sans-serif" font-size="36" 
          fill="white" text-anchor="start" filter="url(#shadow)">
        {current_date}
    </text>
    
    <!-- Zegar analogowy (40% mniejszy niż oryginał, przesunięty na prawą stronę, na prawo od daty/godziny) -->
    <!-- Okrąg tarczy zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="{clock_radius}" 
            fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.8" filter="url(#shadow)"/> <!-- cieńsza krawędź -->
    
    <!-- Środek zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="3" fill="white"/> <!-- mniejszy środek -->
    
    <!-- Znaczniki godzin -->
    <g stroke="white" stroke-width="1.2"> <!-- cieńsze znaczniki -->
        {hour_marks_svg}
    </g>
    
    <!-- Wskazówka godzinowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{hour_x}" y2="{hour_y}" 
          stroke="white" stroke-width="3.6" stroke-linecap="round" filter="url(#shadow)"/> <!-- cieńsza -->
    
    <!-- Wskazówka minutowa - NOWY KOLOR #FFCC00 -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{minute_x}" y2="{minute_y}" 
          stroke="#FFCC00" stroke-width="2.4" stroke-linecap="round" filter="url(#shadow)"/> <!-- cieńsza -->
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
            <!-- Odświeżanie co 10 sekund (bez sekund) -->
            <meta http-equiv="refresh" content="10">
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
                .update-info {
                    background: rgba(255, 204, 0, 0.2);
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    display: inline-block;
                }
                .timer {
                    font-family: monospace;
                    font-size: 1.2em;
                    background: rgba(255,255,255,0.1);
                    padding: 5px 10px;
                    border-radius: 5px;
                    display: inline-block;
                    margin-left: 10px;
                }
                .minute-hand-color {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    background: #FFCC00;
                    border: 1px solid white;
                    vertical-align: middle;
                    margin: 0 5px;
                    border-radius: 3px;
                }
                .size-info {
                    background: rgba(255, 100, 100, 0.2);
                    padding: 10px;
                    border-radius: 5px;
                    margin: 10px 0;
                    display: inline-block;
                }
            </style>
            <script>
                // Timer odliczający do następnego odświeżenia
                let timeLeft = 10;
                
                function updateTimer() {
                    timeLeft--;
                    if (timeLeft <= 0) {
                        timeLeft = 10;
                    }
                    document.getElementById('timer').textContent = timeLeft;
                }
                
                // Uruchom timer po załadowaniu strony
                window.onload = function() {
                    updateTimer();
                    setInterval(updateTimer, 1000);
                };
            </script>
        </head>
        <body>
            <div class="container">
                <h1>⏰ Zegar Analogowy i Cyfrowy (UTC+1)</h1>
                <img src="/time.png" alt="Aktualna godzina" width="880" height="400">
                
                <div class="description">
                    <h2>Opis funkcjonalności:</h2>
                    <div class="features">
                        <div class="feature">
                            <h3>🕐 Zegar Analogowy</h3>
                            <div class="size-info">
                                <strong>NOWOŚĆ: 40% MNIEJSZY!</strong>
                            </div>
                            <p>Po prawej stronie obrazka:</p>
                            <ul>
                                <li>Biała (gruba) - godziny</li>
                                <li><span class="minute-hand-color"></span> Żółta (#FFCC00) - minuty</li>
                                <li>Promień: 48px (było 80px)</li>
                                <li><em>Bez wskazówki sekundowej</em></li>
                            </ul>
                        </div>
                        <div class="feature">
                            <h3>🔢 Czas Cyfrowy</h3>
                            <p><strong>Z LEWEJ STRONY</strong></p>
                            <p>Format: <strong>HH:MM</strong></p>
                            <p>Data: <strong>RRRR-MM-DD</strong></p>
                            <p><em>Bez sekund</em></p>
                            <p>Mniejsza czcionka, lepsze wyrównanie</p>
                        </div>
                        <div class="feature">
                            <h3>⚡ Nowości</h3>
                            <p>Zegar analogowy 40% mniejszy</p>
                            <p>Czas cyfrowy po lewej stronie</p>
                            <p>Żółta wskazówka minutowa</p>
                            <p>Strefa czasowa: UTC+1</p>
                            <p>Lepsze rozmieszczenie elementów</p>
                        </div>
                    </div>
                </div>
                
                <div class="update-info">
                    ⚡ Odświeżanie za: <span id="timer" class="timer">10</span> sekund
                </div>
                
                <p>Bezpośredni link do obrazka: <a href="/time.png">/time.png</a></p>
                <p>Obrazek generowany na żądanie • Odświeżanie co 10 sekund</p>
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