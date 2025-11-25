from flask import Flask, Response
from datetime import datetime

app = Flask(__name__)

def generate_time_image():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="150" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="2"/>
    <text x="50" y="60" font-family="Arial, sans-serif" font-size="24" fill="black">
        Godzina: {current_time}
    </text>
    <text x="50" y="100" font-family="Arial, sans-serif" font-size="18" fill="blue">
        Data: {current_date}
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
            <img src="/time.png" alt="Aktualna godzina">
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
    app.run(host='0.0.0.0', port=5000)