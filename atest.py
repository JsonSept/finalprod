from flask import Flask, request, render_template_string, jsonify
from datetime import datetime
import random
import threading
import time

app = Flask(__name__)

# Simulating a battery storage for the inverter data
battery_storage = []

# Global variables to store current irradiance and total currency amount
current_irradiance = 1000  # Initial dummy value
total_energy_in_currency = 0
currency_rate = 1  # Default currency rate

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
        input, select {
            padding: 10px;
            width: 100%;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 5px;
            margin-bottom: 10px;
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
    </style>
</head>
<body>
    <h1>Solar Inverter Data Input</h1>
    <form method="get">
        <!-- Input fields -->
    </form>

    <div class="chart-container">
        <h2>Energy Output Data</h2>
        <div class="data-box">
            <p>Voltage: {{ data.voltage }} V</p>
            <p>Current: {{ data.current }} A</p>
            <p>Power: {{ data.power }} W</p>
            <p>Temperature: {{ data.temperature }}</p>
            <p>Total Energy Output: {{ data.total_energy_output_kwh }} kWh</p>
            <p>Amount per kWh: <span id="amount_per_kwh">R {{ data.total_energy_output_currency }}</span></p>
            <p>Solar Irradiance: <span id="irradiance">{{ data.irradiance }}</span> W/m²</p>
        </div>
    </div>

    <h2>Live Solar Irradiance</h2>
    <p>Current Solar Irradiance: <span id="live-irradiance">{{ data.irradiance if data else 'Loading...' }}</span> W/m²</p>

    <script>
        function fetchIrradiance() {
            fetch('/get_irradiance')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('live-irradiance').innerText = data.irradiance;
                    fetchUpdatedEnergy(); // Update energy data whenever irradiance changes
                })
                .catch(error => {
                    console.error('Error fetching irradiance:', error);
                });
        }

        function fetchUpdatedEnergy() {
            let panelArea = document.querySelector('[name="panel_area"]').value;
            let numPanels = document.querySelector('[name="num_panels"]').value;
            let efficiency = document.querySelector('[name="efficiency"]').value;
            let power = document.querySelector('[name="power"]').value;
            let currencyRate = document.querySelector('[name="currency_rate"]').value;

            fetch(`/update_energy?panel_area=${panelArea}&num_panels=${numPanels}&efficiency=${efficiency}&power=${power}&currency_rate=${currencyRate}`)
                .then(response => response.json())
                .then(data => {
                    document.getElementById('amount_per_kwh').innerText = `R ${data.total_energy_output_currency}`;
                })
                .catch(error => {
                    console.error('Error fetching updated energy data:', error);
                });
        }
        setInterval(fetchUpdateEnergy, 2000)
        // Fetch irradiance and update energy every 2 seconds
        setInterval(fetchIrradiance, 2000);
    </script>
</body>
</html>

'''

@app.route('/')
def index():
    # Example data to render initially
    data = {
        'voltage': '220',
        'current': '10',
        'power': '2000',
        'temperature': '25°C',
        'total_energy_output_kwh': '5.0',
        'total_energy_output_currency': '100.00',
        'irradiance': current_irradiance
    }
    return render_template_string(HTML_TEMPLATE, data=data)

@app.route('/update_energy', methods=['GET'])
def update_energy():
    global total_energy_in_currency, current_irradiance, currency_rate

    panel_area = float(request.args.get('panel_area'))
    num_panels = int(request.args.get('num_panels'))
    efficiency = float(request.args.get('efficiency')) / 100
    power = float(request.args.get('power'))
    currency_rate = float(request.args.get('currency_rate'))

    total_area = panel_area * num_panels

    # Recalculate total energy and currency
    total_energy_output = (current_irradiance * total_area * efficiency * power) / 1000  # kWh
    total_energy_in_currency += total_energy_output * currency_rate

    return {
        "total_energy_output_kwh": round(total_energy_output, 2),
        "total_energy_output_currency": round(total_energy_in_currency, 2)
    }

@app.route('/get_irradiance', methods=['GET'])
def get_irradiance():
    global current_irradiance
    return {"irradiance": current_irradiance}

def update_irradiance():
    global current_irradiance
    while True:
        # Simulate irradiance changes
        current_irradiance = random.uniform(800, 1200)
        time.sleep(2)  # Update every 2 seconds

if __name__ == '__main__':
    # Start the background thread to update irradiance
    threading.Thread(target=update_irradiance, daemon=True).start()
    app.run(debug=True)
