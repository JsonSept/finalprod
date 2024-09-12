from flask import Flask, request, jsonify
import time

app = Flask(__name__)

# Function to calculate solar panel power
def calculate_power(voltage, current, irradiance, panel_area, efficiency):
    efficiency_in_decimal = efficiency / 100
    power = voltage * current
    total_energy_output = (irradiance * panel_area * efficiency_in_decimal * power) / 1000  # kWh
    return {
        "power_output": power,  # Change key name to power_output
        "total_energy_output": total_energy_output  # Change key name to total_energy_output
    }


@app.route('/panel_data', methods=['GET'])
def panel_data():
    # Simulate solar irradiance
    irradiance = 800 + (200 * time.time() % 10)
    
    # Read parameters from request
    voltage = float(request.args.get('voltage', 12))
    current = float(request.args.get('current', 10))
    panel_area = float(request.args.get('panel_area', 10))
    efficiency = float(request.args.get('efficiency', 20))
    
    # Calculate power output
    result = calculate_power(voltage, current, irradiance, panel_area, efficiency)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Solar panel service running on port 5001
