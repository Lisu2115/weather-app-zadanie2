import os
import datetime
from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

AUTHOR_NAME = "Mikolaj Lis"
PORT = 5000

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Pogoda App</title>
    <style>
        body { font-family: Arial; margin: 40px; background-color: #f0f2f5; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        select, button { padding: 10px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Aplikacja Pogodowa</h1>
        <p>Autor: <b>{{ author }}</b></p>
        <form method="POST">
            <label>Wybierz miasto:</label><br>
            <select name="city">
                <option value="52.2297,21.0122,Warszawa">Warszawa</option>
                <option value="50.0647,19.9450,Kraków">Kraków</option>
                <option value="51.1079,17.0385,Wrocław">Wrocław</option>
                <option value="54.3520,18.6466,Gdańsk">Gdańsk</option>
            </select>
            <button type="submit">Sprawdź pogodę</button>
        </form>

        {% if weather %}
            <hr>
            <h3>Pogoda dla: {{ city_name }}</h3>
            <p>Temperatura: <b>{{ weather['current']['temperature_2m'] }}°C</b></p>
            <p>Wiatr: {{ weather['current']['wind_speed_10m'] }} km/h</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city_name = ""
    if request.method == 'POST':
        data = request.form.get('city').split(',')
        lat, lon, city_name = data[0], data[1], data[2]
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
        response = requests.get(url)
        weather_data = response.json()
    
    return render_template_string(HTML_TEMPLATE, author=AUTHOR_NAME, weather=weather_data, city_name=city_name)

if __name__ == '__main__':
    print(f"--- URUCHOMIENIE APLIKACJI ---")
    print(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Autor: {AUTHOR_NAME}")
    print(f"Port: {PORT}")
    print(f"------------------------------")
    app.run(host='0.0.0.0', port=PORT)
    