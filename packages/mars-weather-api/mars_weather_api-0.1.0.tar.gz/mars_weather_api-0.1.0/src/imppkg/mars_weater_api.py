"""
MarsWeatherAPI
--------------
A Python interface for NASA's InSight Mars Weather API to fetch and display Martian weather data.

Class:
------
MarsWeatherAPI:
    - Interacts with the API to retrieve weather data.

Methods:
--------
__init__(api_key, feedtype='json', version=1.0):
    Initializes the API client.
get_all_weather():
    Fetches all weather data.
get_temps_only():
    Returns temperature data (avg, min, max) for each sol.
get_day(day=0):
    Retrieves weather data for a specific sol.
get_week():
    Retrieves weather data for the last 7 sols.
print_day(day=0):
    Prints formatted weather data for a specific sol.
print_week():
    Prints formatted weather data for the last 7 sols.

Usage:
------
api = MarsWeatherAPI('your_api_key')
api.print_week()
"""
import requests
from datetime import datetime

class MarsWeatherAPI():

    BASE_URL = "https://api.nasa.gov/insight_weather/"

    def __init__(self, api_key:str, feedtype:str='json',version = 1.0):
        self.api_key = api_key
        self.feedtype = feedtype
        self.version = version
        self.data = self.get_all_weather()
    
    def get_all_weather(self):

        params ={
            "api_key": self.api_key,
            "feedtype": self.feedtype,
            "version": self.version
        }

        try:
            response = requests.get(self.BASE_URL , params=params)
            data = response.json()
            return data
        except Exception as e:
            raise e
        
    def get_temps_only(self):
        temps = {}
        for sol_key in self.data['sol_keys']:
            if 'AT' in self.data[sol_key]:
                temps[sol_key] = self.data[sol_key]['AT']
                date = datetime.strptime(self.data[sol_key]['First_UTC'], '%Y-%m-%dT%H:%M:%SZ')
                formatted_date = date.strftime('%b. %d, %Y')
                temps[sol_key][date] = formatted_date
        return temps

    def get_day(self, day:int = 0):
        days = []
        for key in self.data['sol_keys']:
            days.append(self.data[key])
        return days[day]
    
    def get_week(self):
        week = []
        for _ in range(7):
            week.append(self.get_day(_))
        return week
    
    def print_day(self, day:int=0):
        day = self.get_day(day)
        date = datetime.strptime(day['First_UTC'], '%Y-%m-%dT%H:%M:%SZ')
        formatted_date = date.strftime('%b. %d, %Y')
        print(f'{formatted_date}|Avg Temp: {day['AT']['av']}|Min: {day['AT']['mn']}|Max: {day['AT']['mx']}')
    
    def print_week(self):
        for _ in range(7):
            self.print_day(_)