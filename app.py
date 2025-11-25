from flask import Flask, Response
from datetime import datetime
import io
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

def generate_time_image():
    img = Image.new('RGB', (400, 150), color='white')
    draw = ImageDraw.Draw(img)
    
    current_time = datetime.now().strftime("%H:%M:%S")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 20)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    draw.text((50, 30), f"Godzina: {current_time}", fill='black', font=font_large)
    draw.text((50, 80), f"Data: {current_date}", fill='blue', font=font_small)
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr

@app.route('/')
def home():
    return """
    <html>
        <body>
            <h1>Obrazek z godziną</h1>
            <img src="/time.png" style="border: 1px solid #ccc;">
            <p>Obrazek aktualizuje się przy każdym odświeżeniu</p>
            <p>Możesz też użyć bezpośredniego linku: <a href="/time.png">/time.png</a></p>
        </body>
    </html>
    """

@app.route('/time.png')
def get_time_image():
    img_bytes = generate_time_image()
    return Response(img_bytes.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)