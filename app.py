from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
import cairosvg
import base64
import math

app = Flask(__name__)


def generate_image(save_to_file=False):
    """
    Generuje obrazek zegara.

    Args:
        save_to_file (bool): Jeśli True, zapisuje obrazek do pliku test.png

    Returns:
        bytes: Obrazek w formacie PNG
    """
    tz = timezone(timedelta(hours=1))
    now = datetime.now(tz)

    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%Y-%m-%d")

    hours = now.hour % 12
    minutes = now.minute

    hour_angle = (hours * 30) + (minutes * 0.5)
    minute_angle = minutes * 6

    cx, cy = 540, 340
    r = 48

    def polar(angle_deg, length):
        """Konwertuje kąt i długość na współrzędne kartezjańskie."""
        rad = math.radians(angle_deg - 90)  # -90° aby 0° było na górze
        return cx + length * math.cos(rad), cy + length * math.sin(rad)

    # Współrzędne końców wskazówek
    hx, hy = polar(hour_angle, r * 0.5)
    mx, my = polar(minute_angle, r * 0.7)

    bg = ""
    if os.path.exists('static/background.jpg'):
        try:
            with open('static/background.jpg', 'rb') as f:
                bg = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
        except:
            pass

    # Rysowanie kresek godzinowych
    marks = []
    for i in range(12):
        angle = i * 30  # 0°, 30°, 60°, ... 330°
        x1, y1 = polar(angle, r - 6)
        x2, y2 = polar(angle, r)
        marks.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')

    svg = f'''<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg">
    <!-- Tło -->
    <rect width="880" height="400" fill="#58294D"/>
    {f'<image href="{bg}" width="880" height="400"/>' if bg else ""}

    <!-- Czas i data -->
    <text x="250" y="340" font-family="Verdana" font-size="60" fill="white" text-anchor="start" font-weight="bold">{time_str}</text>
    <text x="250" y="390" font-family="Verdana" font-size="32" fill="white" text-anchor="start">{date_str}</text>

    <!-- Tarcza zegara -->
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.8"/>

    <!-- Kreski godzinowe -->
    <g stroke="white" stroke-width="1.2" shape-rendering="crispEdges">
        {"".join(marks)}
    </g>

    <!-- Środek tarczy -->
    <circle cx="{cx}" cy="{cy}" r="3" fill="white"/>

    <!-- Wskazówka godzinowa -->
    <line x1="{cx}" y1="{cy}" x2="{hx:.1f}" y2="{hy:.1f}" 
          stroke="white" stroke-width="3.6" stroke-linecap="round"/>

    <!-- Wskazówka minutowa -->
    <line x1="{cx}" y1="{cy}" x2="{mx:.1f}" y2="{my:.1f}" 
          stroke="#FFCC00" stroke-width="2.4" stroke-linecap="round"/>
</svg>'''

    png = cairosvg.svg2png(bytestring=svg.encode())

    # Zapis do pliku jeśli wymagane
    if save_to_file:
        with open('test.png', 'wb') as f:
            f.write(png)

    return png


# Wygeneruj test.png przed uruchomieniem serwera
generate_image(save_to_file=True)


@app.route('/')
def home():
    return '''
    <html>
        <head>
            <title>Zegar</title>
            <meta http-equiv="refresh" content="10">
            <style>
                body {{
                    margin: 0;
                    padding: 10px;
                    background: #58294D;
                    text-align: center;
                    font-family: Arial, sans-serif;
                }}
                img {{
                    display: block;
                    margin: 0 auto;
                    max-width: 100%;
                    border-radius: 8px;
                }}
                .info {{
                    color: white;
                    margin-top: 15px;
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .container {{
                    max-width: 900px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .timestamp {{
                    color: #FFCC00;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <img src="/time.png" alt="Aktualny czas">
                <div class="info">
                    Odświeżanie co 10 sekund • UTC+1 • 
                    <span class="timestamp">{}</span>
                </div>
            </div>
        </body>
    </html>'''.format(datetime.now(timezone(timedelta(hours=1))).strftime("%Y-%m-%d %H:%M:%S"))


@app.route('/time.png')
def get_time_image():
    png = generate_image()
    resp = Response(png, mimetype='image/png')
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)