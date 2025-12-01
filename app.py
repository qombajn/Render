from flask import Flask, Response
from datetime import datetime, timezone, timedelta
import os
import cairosvg
import base64
import math

app = Flask(__name__)

def generate_time_image():
    tz = timezone(timedelta(hours=1))
    now = datetime.now(tz)
    
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%Y-%m-%d")
    
    hours = now.hour % 12
    minutes = now.minute
    
    hour_angle = (hours * 30) + (minutes * 0.5)
    minute_angle = minutes * 6
    
    cx, cy = 520, 340
    r = 48
    
    def polar(angle_deg, length):
        rad = math.radians(angle_deg - 90)
        return cx + length * math.cos(rad), cy + length * math.sin(rad)
    
    hx, hy = polar(hour_angle, r * 0.5)
    mx, my = polar(minute_angle, r * 0.7)
    
    bg = ""
    if os.path.exists('static/background.jpg'):
        try:
            with open('static/background.jpg', 'rb') as f:
                bg = f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
        except:
            pass

    marks = []
    for i in range(12):
        a = math.radians(i * 30 - 90)
        x1 = cx + (r - 6) * math.cos(a)
        y1 = cy + (r - 6) * math.sin(a)
        x2 = cx + r * math.cos(a)
        y2 = cy + r * math.sin(a)
        marks.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    
    svg = f'''<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg">
    <defs><filter id="s"><feOffset dx="3" dy="3"/><feGaussianBlur stdDeviation="5"/></filter></defs>
    <rect width="880" height="400" fill="#58294D"/>
    {f'<image href="{bg}" width="880" height="400"/>' if bg else ""}
    <text x="250" y="340" font-family="Verdana" font-size="60" fill="white" text-anchor="start" font-weight="bold" filter="url(#s)">{time_str}</text>
    <text x="250" y="390" font-family="Verdana" font-size="32" fill="white" text-anchor="start" filter="url(#s)">{date_str}</text>
    <circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="1.8" filter="url(#s)"/>
    <circle cx="{cx}" cy="{cy}" r="3" fill="white"/>
    <g stroke="white" stroke-width="1.2">{"".join(marks)}</g>
    <line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="white" stroke-width="3.6" stroke-linecap="round" filter="url(#s)"/>
    <line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#FFCC00" stroke-width="2.4" stroke-linecap="round" filter="url(#s)"/>
</svg>'''
    
    return cairosvg.svg2png(bytestring=svg.encode())

@app.route('/')
def home():
    return '''
    <html><head><title>Zegar</title><meta http-equiv="refresh" content="10"><style>
    body{margin:0;padding:10px;background:#58294D;text-align:center;font-family:Arial;}
    img{display:block;margin:0 auto;max-width:100%;}
    .info{color:white;margin-top:10px;font-size:14px;}</style></head>
    <body><img src="/time.png"><div class="info">Odświeżanie co 10 sekund • UTC+1</div></body></html>'''

@app.route('/time.png')
def get_time_image():
    png = generate_time_image()
    resp = Response(png, mimetype='image/png')
    resp.headers['Cache-Control'] = 'no-cache'
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)