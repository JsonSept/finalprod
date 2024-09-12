import requests
import math

# Replace with your OpenWeatherMap API key
API_KEY = 'e945d7f71eb0e5e621a7dfcce2cb1a43'
LATITUDE = '-33.985744036973834'
LONGITUDE = '18.493045393016516'

def get_weather_data(api_key, lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
    response = requests.get(url)
    return response.json()

def calculate_solar_irradiance(weather_data):
    # Extract necessary data
    cloud_cover = weather_data['clouds']['all'] / 100  # Convert percentage to fraction
    solar_constant = 1361  # Solar constant in W/m²
    zenith_angle = 90 - weather_data['sys']['sunrise']  # Simplified zenith angle calculation

    # Clear sky irradiance
    clear_sky_irradiance = solar_constant * math.cos(math.radians(zenith_angle))

    # Adjust for cloud cover
    irradiance = clear_sky_irradiance * (1 - cloud_cover)

    return irradiance

def main():
    weather_data = get_weather_data(API_KEY, LATITUDE, LONGITUDE)
    irradiance = calculate_solar_irradiance(weather_data)
    print(f'Solar Irradiance: {irradiance:.2f} W/m²')

if __name__ == '__main__':
    main()
