from flask import Flask, Response
from datetime import datetime
import os

app = Flask(__name__)

def generate_time_image():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="880" height="400" xmlns="http://www.w3.org/2000/svg">
    <image href="/static/background.jpg" width="880" height="400"/>
    <text x="780" y="350" font-family="Arial, sans-serif" font-size="36" fill="white" text-anchor="end">
        {current_time}
    </text>
    <text x="780" y="390" font-family="Arial, sans-serif" font-size="24" fill="white" text-anchor="end">
        {current_date}
    </text>
</svg>'''
    return svg_content

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
            <h1>🕐 Obrazek z aktualną godziną</h1>
            <img src="/time.png" alt="Aktualna godzina" width="880" height="400">
            <p>Obrazek automatycznie się odświeża co sekundę</p>
            <p>Bezpośredni link do obrazka: <a href="/time.png">/time.png</a></p>
        </body>
    </html>
    '''

@app.route('/time.png')
def get_time_image():
    svg_content = generate_time_image()
    response = Response(svg_content, mimetype='image/svg+xml')
    # Zapobieganie cache'owaniu
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    # Utwórz katalog static jeśli nie istnieje
    os.makedirs('static', exist_ok=True)
    app.run(host='0.0.0.0', port=5000)