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
    
    # Współrzędne środka zegara analogowego (przesunięty na prawą stronę, bardziej w prawo)
    clock_center_x = 680  # Przesunięty bardziej w prawo
    clock_center_y = 320
    clock_radius = 64  # 80 * 0.8 = 64 (20% mniejsze)
    
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
        x1 = clock_center_x + (clock_radius - 8) * math.cos(angle)  # Dostosowane do mniejszego zegara
        y1 = clock_center_y + (clock_radius - 8) * math.sin(angle)
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
    
    <!-- Zegar analogowy (20% mniejszy, przesunięty na prawą stronę, na prawo od daty/godziny) -->
    <!-- Okrąg tarczy zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="{clock_radius}" 
            fill="rgba(255,255,255,0.15)" stroke="white" stroke-width="2.4" filter="url(#shadow)"/> <!-- cieńsza krawędź -->
    
    <!-- Środek zegara -->
    <circle cx="{clock_center_x}" cy="{clock_center_y}" r="4" fill="white"/> <!-- mniejszy środek -->
    
    <!-- Znaczniki godzin -->
    <g stroke="white" stroke-width="1.6"> <!-- cieńsze znaczniki -->
        {hour_marks_svg}
    </g>
    
    <!-- Wskazówka godzinowa -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{hour_x}" y2="{hour_y}" 
          stroke="white" stroke-width="4.8" stroke-linecap="round" filter="url(#shadow)"/> <!-- cieńsza -->
    
    <!-- Wskazówka minutowa - NOWY KOLOR #FFCC00 -->
    <line x1="{clock_center_x}" y1="{clock_center_y}" 
          x2="{minute_x}" y2="{minute_y}" 
          stroke="#FFCC00" stroke-width="3.2" stroke-linecap="round" filter="url(#shadow)"/> <!-- cieńsza -->
</svg>'''
    
    # Konwersja SVG do PNG
    png_data = cairosvg.svg2png(bytestring=svg_content.encode('utf-8'))
    return png_data