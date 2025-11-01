import requests
import os
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

class WeatherService:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '7b709f94ee9d30626b86cd2e167160c6')
        print(f"Weather API Key loaded: {self.api_key[:8]}...")  # Debug: show first 8 chars
        self.base_url = 'https://api.openweathermap.org/data/2.5'

    def get_weather_data(self, location, days=30):
        """
        Get weather data for a location over the past days
        Returns average rainfall and temperature
        """
        try:
            # Get current weather
            current_url = f"{self.base_url}/weather?q={location}&appid={self.api_key}&units=metric"
            current_response = requests.get(current_url)
            current_response.raise_for_status()
            current_data = current_response.json()

            # Get forecast data (5 days)
            forecast_url = f"{self.base_url}/forecast?q={location}&appid={self.api_key}&units=metric"
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Calculate averages
            rainfall_total = 0
            temp_total = 0
            count = 0

            # Add current temperature
            temp_total += current_data['main']['temp']
            count += 1

            # Add forecast data (only if available)
            if 'list' in forecast_data and len(forecast_data['list']) > 0:
                for item in forecast_data['list'][:8]:  # Next 24 hours (3-hour intervals)
                    temp_total += item['main']['temp']
                    # Check for rain
                    if 'rain' in item and '3h' in item['rain']:
                        rainfall_total += item['rain']['3h']
                    count += 1
            else:
                print("No forecast data available, using only current weather")

            avg_temp = temp_total / count if count > 0 else current_data['main']['temp']
            avg_rainfall = rainfall_total  # This is for 24 hours, we'll extrapolate

            return {
                'success': True,
                'avg_temperature': round(avg_temp, 1),
                'avg_rainfall': round(avg_rainfall, 1),
                'location': current_data['name'],
                'country': current_data['sys']['country'],
                'description': current_data['weather'][0]['description']
            }

        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Weather API error: {str(e)}"
            }
        except KeyError as e:
            return {
                'success': False,
                'error': f"Invalid location or API response: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def get_historical_weather_data(self, location, start_date, end_date):
        """
        Get historical weather data for a location between start_date and end_date
        Returns average rainfall and temperature over the period
        Note: Free OpenWeatherMap API only provides last 5 days of historical data
        """
        try:
            from datetime import datetime, timedelta

            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            current_timestamp = int(datetime.now().timestamp())

            # OpenWeatherMap free tier limitation: only last 5 days
            five_days_ago = current_timestamp - (5 * 24 * 60 * 60)

            # If start_date is within last 5 days, we can get historical data
            if start_timestamp >= five_days_ago:
                return self._get_openweather_historical(location, start_timestamp, end_timestamp)
            else:
                # For longer periods, use current weather + seasonal estimates
                return self._get_seasonal_weather_estimate(location, start_date, end_date)

        except Exception as e:
            return {
                'success': False,
                'error': f"Historical weather error: {str(e)}"
            }

    def _get_openweather_historical(self, location, start_timestamp, end_timestamp):
        """Get historical data using OpenWeatherMap One Call API (requires paid plan for full access)"""
        try:
            # For free tier, we can only get current + forecast
            # This is a limitation we'll work with
            current_weather = self.get_weather_data(location, days=1)

            if not current_weather['success']:
                return current_weather

            # Get coordinates for the location
            geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.api_key}"
            geo_response = requests.get(geo_url)
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data:
                return {
                    'success': False,
                    'error': 'Location not found for historical data'
                }

            lat, lon = geo_data[0]['lat'], geo_data[0]['lon']

            # Try to get historical data (this might fail on free tier)
            historical_url = f"https://api.openweathermap.org/data/3.0/onecall/timemachine?lat={lat}&lon={lon}&dt={start_timestamp}&appid={self.api_key}&units=metric"

            historical_response = requests.get(historical_url)
            if historical_response.status_code == 200:
                historical_data = historical_response.json()

                # Process historical data
                temps = []
                rains = []

                if 'data' in historical_data:
                    for entry in historical_data['data']:
                        temps.append(entry['temp'])
                        if 'rain' in entry:
                            rains.append(entry['rain'].get('1h', 0))
                        else:
                            rains.append(0)

                avg_temp = sum(temps) / len(temps) if temps else current_weather['avg_temperature']
                avg_rain = sum(rains) / len(rains) * 24 if rains else current_weather['avg_rainfall']  # Convert hourly to daily

                return {
                    'success': True,
                    'avg_temperature': round(avg_temp, 1),
                    'avg_rainfall': round(avg_rain, 1),
                    'location': current_weather['location'],
                    'country': current_weather['country'],
                    'description': 'Historical data (limited to 5 days)',
                    'data_period': 'historical'
                }
            else:
                # Fall back to current weather with note
                return {
                    'success': True,
                    'avg_temperature': current_weather['avg_temperature'],
                    'avg_rainfall': current_weather['avg_rainfall'],
                    'location': current_weather['location'],
                    'country': current_weather['country'],
                    'description': 'Current weather (historical data requires paid API)',
                    'data_period': 'current',
                    'note': 'Free tier limitation: Using current weather as approximation for historical period'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f"Historical API error: {str(e)}"
            }

    def _get_seasonal_weather_estimate(self, location, start_date, end_date):
        """Provide seasonal weather estimates when historical data is not available"""
        from datetime import datetime

        try:
            # Parse dates to determine season
            start = datetime.strptime(start_date, '%Y-%m-%d')
            month = start.month

            # Seasonal averages for Nigeria (can be improved with more data)
            seasonal_data = {
                # Dry season (November - February)
                (11, 12, 1, 2): {'temp': 32, 'rain': 5},
                # Pre-monsoon (March - April)
                (3, 4): {'temp': 34, 'rain': 15},
                # Monsoon season (May - October)
                (5, 6, 7, 8, 9, 10): {'temp': 27, 'rain': 180}
            }

            # Find matching season
            for months, data in seasonal_data.items():
                if month in months:
                    seasonal_temp = data['temp']
                    seasonal_rain = data['rain']
                    break
            else:
                seasonal_temp = 30  # Default
                seasonal_rain = 100  # Default

            # Get current location data
            current_weather = self.get_weather_data(location, days=1)

            return {
                'success': True,
                'avg_temperature': seasonal_temp,
                'avg_rainfall': seasonal_rain,
                'location': current_weather.get('location', location.split(',')[0]),
                'country': current_weather.get('country', 'Nigeria'),
                'description': f'Seasonal estimate for {start.strftime("%B")}',
                'data_period': 'seasonal',
                'note': 'Using seasonal averages due to API limitations'
            }

        except Exception as e:
            return {
                'success': False,
                'error': f"Seasonal estimate error: {str(e)}"
            }

    def get_location_suggestions(self, query):
        """
        Get location suggestions for autocomplete
        """
        try:
            url = f"https://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={self.api_key}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            suggestions = []
            for item in data:
                suggestions.append({
                    'name': item['name'],
                    'country': item['country'],
                    'full_name': f"{item['name']}, {item['country']}"
                })

            return suggestions

        except Exception as e:
            return []

    def get_weather_by_coordinates(self, lat, lon):
        """
        Get weather data by coordinates
        """
        try:
            # Get current weather
            url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            return {
                'success': True,
                'location': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity']
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global weather service instance
weather_service = WeatherService()