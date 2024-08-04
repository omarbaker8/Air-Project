from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class APIResponse(models.Model):
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"API Response at {self.timestamp}"

class AirQualityData(models.Model):
    api_response = models.ForeignKey(APIResponse, on_delete=models.CASCADE, related_name='air_quality_data')
    lat = models.FloatField()
    lon = models.FloatField()
    uid = models.IntegerField()
    aqi = models.CharField(max_length=10)
    station_name = models.CharField(max_length=255)
    station_time = models.DateTimeField()

    def __str__(self):
        return f"{self.station_name} - AQI: {self.aqi}"

    class Meta:
        verbose_name_plural = "Air Quality Data"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    station_uid = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'station_uid'], name='unique_user_station')
        ]

    def __str__(self):
        return f"{self.user.username} - Station UID: {self.station_uid}"

def save_air_quality_data(data):
    if data['status'] == 'ok':
        # Save the API response
        api_response = APIResponse.objects.create(status=data['status'])

        # Save each air quality data point
        for item in data['data']:
            AirQualityData.objects.create(
                api_response=api_response,
                lat=item['lat'],
                lon=item['lon'],
                uid=item['uid'],
                aqi=item['aqi'],
                station_name=item['station']['name'],
                station_time=datetime.strptime(item['station']['time'], "%Y-%m-%dT%H:%M:%S%z")
            )
        return api_response
    else:
        # Handle error case
        print(f"Error in API response: {data['status']}")
        api_response = APIResponse.objects.create(status=data['status'])
        return None
    
class MedicalCondition(models.Model):
    CONDITION_CHOICES = [
        ('COPD', 'Chronic Obstructive Disease'),
        ('ASTHMA', 'Asthma'),
        ('CF', 'Cystic Fibrosis'),
        ('SA', 'Sleep Apnea'),
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    description = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_condition_display()}"

    class Meta:
        unique_together = ['user', 'condition']

class DailyConditionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    medical_condition = models.ForeignKey(MedicalCondition, on_delete=models.CASCADE)
    date = models.DateTimeField()
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.medical_condition.get_condition_display()} - {self.date} - Rating: {self.rating}"