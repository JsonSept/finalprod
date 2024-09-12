from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# Get solar panel data from the Solar Panel Service
def fetch_solar_panel_data():
    panel_service_url = 'http://localhost:5001/panel_data'
    response = requests.get(panel_service_url, params={
        'voltage': 24,  # Example values, can be dynamic
        'current': 10,
        'panel_area': 15,
        'efficiency': 20
    })
    
    if response.status_code == 200:
        return response.json()
    return None

@app.route('/', methods=['GET'])
def home():
    # Fetch data from solar panel service
    panel_data = fetch_solar_panel_data()
    
    if panel_data:
        power_output = panel_data['power_output_watts']
        total_energy_output = panel_data['total_energy_output_kwh']
        
        return jsonify({
            'inverter_status': 'active',
            'solar_panel_power_output_watts': power_output,
            'solar_panel_total_energy_kwh': total_energy_output
        })
    return jsonify({'error': 'Failed to get solar panel data'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Inverter service running on port 5000
