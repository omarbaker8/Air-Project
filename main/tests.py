from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import APIResponse, AirQualityData, Favorite, MedicalCondition, DailyConditionRating, save_air_quality_data

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.api_response = APIResponse.objects.create(status='ok')
        self.air_quality_data = AirQualityData.objects.create(
            api_response=self.api_response,
            lat=50.4234,
            lon=-52.0060,
            uid=12345,
            aqi='50',
            station_name='Omar Test Station',
            station_time= timezone.now()
        )

    def test_api_response_creation(self):
        self.assertEqual(str(self.api_response), f"API Response at {self.api_response.timestamp}")

    def test_air_quality_data_creation(self):
        self.assertEqual(str(self.air_quality_data), "Test Station - AQI: 50")

    def test_favorite_creation(self):
        favorite = Favorite.objects.create(user=self.user, station_uid=12345)
        self.assertEqual(str(favorite), "testuser - Station UID: 12345")

    def test_favorite_unique_constraint(self):
        Favorite.objects.create(user=self.user, station_uid=12345)
        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.user, station_uid=12345)

    def test_save_air_quality_data(self):
        data = {
            'status': 'ok',
            'data': [
                {
                    'lat': 40.7128,
                    'lon': -74.0060,
                    'uid': 54321,
                    'aqi': '75',
                    'station': {
                        'name': 'New Test Station',
                        'time': timezone.now().strftime("%Y-%m-%dT%H:%M:%S%z")  # Convert to string
                    }
                }
            ]
        }
        api_response = save_air_quality_data(data)
        self.assertIsNotNone(api_response)
        self.assertEqual(AirQualityData.objects.count(), 2)  # 1 from setUp + 1 new

    def test_save_air_quality_data_error(self):
        data = {'status': 'error'}
        api_response = save_air_quality_data(data)
        self.assertIsNone(api_response)

    def test_medical_condition_creation(self):
        condition = MedicalCondition.objects.create(user=self.user, condition='ASTHMA')
        self.assertEqual(str(condition), "testuser - Asthma")

    def test_medical_condition_unique_constraint(self):
        MedicalCondition.objects.create(user=self.user, condition='ASTHMA')
        with self.assertRaises(IntegrityError):
            MedicalCondition.objects.create(user=self.user, condition='ASTHMA')

    def test_daily_condition_rating_creation(self):
        condition = MedicalCondition.objects.create(user=self.user, condition='COPD')
        rating = DailyConditionRating.objects.create(
            user=self.user,
            medical_condition=condition,
            date=timezone.now(),
            rating=7
        )
        self.assertEqual(str(rating), f"testuser - Chronic Obstructive Disease - {rating.date} - Rating: 7")

    def test_daily_condition_rating_validation(self):
        condition = MedicalCondition.objects.create(user=self.user, condition='COPD')
        with self.assertRaises(ValidationError):
            rating = DailyConditionRating(
                user=self.user,
                medical_condition=condition,
                date=timezone.now(),
                rating=11  # Should raise ValidationError (max is 10)
            )
            rating.full_clean()