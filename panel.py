from flask import Flask, request, render_template_string
from datetime import datetime
import requests
import random
import threading
import time

app = Flask(__name__)

# Simulating a battery storage for the inverter data
battery_storage = []

# Global variable to store the current irradiance
current_irradiance = 1000  # Initial dummy value

# Example HTML template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Solar Inverter Simulation</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #f0f4f8, #d9e2ec);
            color: #333;
            margin: 0;
            padding: 20px;
        }
        h1, h2 {
            text-align: center;
            color: #2c3e50;
        }
        form {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 0 auto;
        }
        label {
            display: block;
            font-weight: 500;
            margin: 15px 0 5px;
        }
        input {
            padding: 10px;
            width: 100%;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        button {
            padding: 12px 20px;
            background-color: #3498db;
            color: #fff;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 10px;
        }
        button:hover {
            background-color: #2980b9;
        }
        .chart-container {
            background-color: #fff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 20px auto;
        }
        .data-box {
            background-color: #eaf1f8;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .data-box p {
            margin: 5px 0;
            font-weight: 500;
        }
        #live-irradiance {
            font-weight: bold;
            color: #16a085;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background-color: #ecf0f1;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
    </style>
</head>
<body>
    <h1>Solar Inverter Data Input</h1>
    <form method="get">
        <label for="voltage">Voltage (V):</label>
            <select name="voltage" required>
                <option value="12">12V DC</option>
                <option value="24">24V DC</option>
                <option value="48">48V DC</option>
                <option value="96">96V DC</option>
                <option value="200">200V DC</option>
                <option value="400">400V DC</option>
                <option value="600">600V DC</option>
            </select>

        <label for="current">Current (A):</label>
            <select name="current" required>
                <option value="5">5A</option>
                <option value="10">10A</option>
                <option value="15">15A</option>
                <option value="20">20A</option>
                <option value="25">25A</option>
                <option value="30">30A</option>
                <option value="40">40A</option>
                <option value="50">50A</option>
            </select>

        <label for="power">Power (W):</label>
            <select name="power" required>
                <option value="1000">1 kW</option>
                <option value="2000">2 kW</option>
                <option value="3000">3 kW</option>
                <option value="5000">5 kW</option>
                <option value="10000">10 kW</option>
                <option value="15000">15 kW</option>
                <option value="20000">20 kW</option>
                <option value="30000">30 kW</option>
                <option value="50000">50 kW</option>
            </select>


        
            <label for="panel_area">Panel Area (m²):</label>
            <select name="panel_area" required>
                <option value="1">1 m²</option>
                <option value="2">2 m²</option>
                <option value="3">3 m²</option>
                <option value="5">5 m²</option>
                <option value="10">10 m²</option>
                <option value="20">20 m²</option>
                <option value="30">30 m²</option>
                <option value="50">50 m²</option>
                <option value="100">100 m²</option>
            </select>

        <label for="efficiency">Efficiency (%):</label>
            <select name="efficiency" required>
                <option value="15">15%</option>
                <option value="16">16%</option>
                <option value="17">17%</option>
                <option value="18">18%</option>
                <option value="19">19%</option>
                <option value="20">20%</option>
                <option value="21">21%</option>
                <option value="22">22%</option>
            </select>
            
        <label for="currency_rate">Currency Rate (per kWh):</label>
        <input type="number" step="0.01" name="currency_rate" required>

        <label for="num_panels">Number of Panels:</label>
        <input type="number" step="1" name="num_panels" required>

        <button type="submit">Submit</button>
    </form>

    {% if data %}
        <div class="chart-container">
            <h2>Energy Output Data</h2>
            <div class="data-box">
                <p>Voltage: {{ data.voltage }} V</p>
                <p>Current: {{ data.current }} A</p>
                <p>Power: {{ data.power }} W</p>
                <p>Temperature: {{ data.temperature }}</p>
                <p>Total Energy Output: {{ data.total_energy_output_kwh }} kWh</p>
                <p>Amount per kWh: R {{ data.total_energy_output_currency }}</p>
                <p>Solar Irradiance: <span id="irradiance">{{ data.irradiance }}</span> W/m²</p>  <!-- Irradiance -->
            </div>
        </div>
    {% endif %}

    <h2>Live Solar Irradiance</h2>
    <p>Current Solar Irradiance: <span id="live-irradiance">{{ data.irradiance if data else 'Loading...' }}</span> W/m²</p>

    <script>
        // JavaScript to fetch and update irradiance every 10 seconds
        function fetchIrradiance() {
            fetch('/get_irradiance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('live-irradiance').innerText = data.irradiance;
                })
                .catch(error => {
                    console.error('Error fetching irradiance:', error);
                });
        }

        // Update every 1.5 seconds
        setInterval(fetchIrradiance, 1500);
    </script>

    {% if battery_storage %}
        <h2>Stored Data</h2>
        <ul>
            {% for entry in battery_storage %}
                <li>{{ entry.timestamp }} - {{ entry.voltage }} V, {{ entry.current }} A, {{ entry.power }} W, {{ entry.total_energy_output_kwh }} kWh, R{{ entry.total_energy_output_currency }} (in currency), {{ entry.irradiance }} W/m²</li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
'''


# Function to get the current temperature using the OpenWeatherMap API
def get_temperature():
    API_KEY = 'e945d7f71eb0e5e621a7dfcce2cb1a43'
    CITY = 'Cape Town'
    URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

    try:
        response = requests.get(URL)
        data = response.json()
        temperature = data['main']['temp']
        return temperature
    except Exception as e:
        print(f"Error getting temperature: {e}")
        return None
@app.route('/get_irradiance', methods=['GET'])
def get_irradiance():
    global current_irradiance
    return {"irradiance": round(current_irradiance, 2)}

# Function to update the solar irradiance data periodically
def update_irradiance():
    global current_irradiance
    while True:
        # Simulate irradiance between 800 and 1200 W/m² (you can change the range)
        current_irradiance = random.uniform(800, 1200)
        time.sleep(2)  # Update every 60 seconds

# Start the irradiance update in a background thread
irradiance_thread = threading.Thread(target=update_irradiance)
irradiance_thread.daemon = True  # Daemonize the thread to terminate when the app stops
irradiance_thread.start()

# Function to generate solar inverter data
def generate_data(voltage, current, power, panel_area, num_panels, efficiency, currency_rate):
    current_time = datetime.now()
    openweather_temp = get_temperature()

    # Use the dynamically updated solar irradiance value
    global current_irradiance
    efficiency_in_decimal = efficiency / 100
    
    # Calculate total surface area
    total_area = panel_area * num_panels
    
    # Calculate total energy in kWh using the current irradiance value
    total_energy_output = (current_irradiance * total_area * efficiency_in_decimal * power) / 1000  # kWh
    
    # Calculate energy output in currency
    total_energy_in_currency = total_energy_output * currency_rate

    data = {
        "timestamp": current_time.isoformat(),
        "voltage": voltage,
        "current": current,
        "power": power,
        "temperature": openweather_temp if openweather_temp is not None else "N/A",
        "total_energy_output_kwh": round(total_energy_output, 2),
        "total_energy_output_currency": round(total_energy_in_currency, 2),
        "irradiance": round(current_irradiance, 2)
    }

    # Store data in battery storage
    battery_storage.append(data)
    return data

@app.route('/', methods=['GET'])
def home():
    voltage = request.args.get('voltage')
    current = request.args.get('current')
    power = request.args.get('power')
    panel_area = request.args.get('panel_area')
    num_panels = request.args.get('num_panels')
    efficiency = request.args.get('efficiency')
    currency_rate = request.args.get('currency_rate')

    data = None
    if voltage and current and power and panel_area and num_panels and efficiency and currency_rate:
        # Convert input to float
        voltage = float(voltage)
        current = float(current)
        power = float(power)
        panel_area = float(panel_area)
        num_panels = int(num_panels)  # Convert to integer
        efficiency = float(efficiency)
        currency_rate = float(currency_rate)
        
        # Generate data using input values and store in battery
        data = generate_data(voltage, current, power, panel_area, num_panels, efficiency, currency_rate)
    
    return render_template_string(HTML_TEMPLATE, data=data, battery_storage=battery_storage)
@app.route('/update_energy', methods=['GET'])
def update_energy():
    panel_area = float(request.args.get('panel_area'))
    num_panels = int(request.args.get('num_panels'))
    efficiency = float(request.args.get('efficiency')) / 100
    power = float(request.args.get('power'))
    currency_rate = float(request.args.get('currency_rate'))

    # Use the updated solar irradiance
    global current_irradiance
    total_area = panel_area * num_panels

    # Recalculate total energy and currency
    total_energy_output = (current_irradiance * total_area * efficiency * power) / 1000  # kWh
    total_energy_in_currency = total_energy_output * currency_rate

    return {
        "total_energy_output_kwh": round(total_energy_output, 2),
        "total_energy_output_currency": round(total_energy_in_currency, 2)
    }

if __name__ == '__main__':
    app.run(debug=True)
