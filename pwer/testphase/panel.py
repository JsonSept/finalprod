from flask import Flask, render_template, jsonify
import time

app = Flask(__name__)

# Function to simulate solar irradiation
def simulate_solar_irradiation():
    return 800 + (200 * time.time() % 10)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/panel_data', methods=['GET'])
def panel_data():
    # Simulate solar irradiation
    irradiation = simulate_solar_irradiation()
    return jsonify({'irradiation': irradiation})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
