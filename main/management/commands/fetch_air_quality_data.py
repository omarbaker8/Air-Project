from django.core.management.base import BaseCommand
import requests
from main.models import save_air_quality_data
import os

# python manage.py fetch_air_quality_data cron job
class Command(BaseCommand):
    help = 'Fetches air quality data'

    def handle(self, *args, **kwargs):
        # api_token = os.environ.get('API_TOKEN')
        api_token = os.environ.get('WAQI_API_TOKEN')
        response = requests.get(f'https://api.waqi.info/map/bounds/?token={api_token}&latlng=51.4,-10.5,55.4,-5.4')
        data = response.json()

        api_response = save_air_quality_data(data)

        if api_response is None:
            self.stdout.write(self.style.ERROR('Error saving data'))
        else:
            self.stdout.write(self.style.SUCCESS('Data saved successfully'))