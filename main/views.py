from django.views.generic import TemplateView
import folium
from .utils import fetch_air_quality_data, fetch_air_quality_data_non_auth
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_GET, require_POST
from django.contrib.auth.decorators import login_required
from .models import Favorite, AirQualityData, APIResponse , MedicalCondition, DailyConditionRating
from django.db.models import Avg, OuterRef, Subquery , Q
from django.db.models.functions import TruncDay, Cast
from django_ip_geolocation.decorators import with_ip_geolocation
from django.db.models import IntegerField
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime



#Home
class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the most recent successful API response
        latest_response = APIResponse.objects.filter(status='ok').order_by('-timestamp').first()

        if latest_response:
            # Get all AirQualityData associated with the latest successful API response
            latest_data = AirQualityData.objects.filter(api_response=latest_response)

            # Total Live Stations
            context['total_live_stations'] = latest_data.values('uid').distinct().count()
            print("---------------------------------------------------------------------------------------")
            print("\033[92m" + f"Total Live Stations: {context['total_live_stations']}" + "\033[0m")

            # Highest and Lowest AQI with station names
            latest_data_with_int_aqi = latest_data.annotate(aqi_int=Cast('aqi', IntegerField()))
            
            highest_aqi_data = latest_data_with_int_aqi.order_by('-aqi_int').first()
            # Filter out entries where aqi is not a valid number
            lowest_aqi_data = latest_data_with_int_aqi.filter(
                Q(aqi_int__isnull=False) & ~Q(aqi_int__exact=0)
            ).order_by('aqi_int').first()

            if highest_aqi_data and lowest_aqi_data:
                context['highest_aqi'] = {
                    'value': highest_aqi_data.aqi,
                    'station': highest_aqi_data.station_name
                }
                context['lowest_aqi'] = {
                    'value': lowest_aqi_data.aqi,
                    'station': lowest_aqi_data.station_name
                }
                print("\033[92m" + f"Highest AQI: {context['highest_aqi']['value']} at {context['highest_aqi']['station']}" + "\033[0m")
                print("\033[92m" + f"Lowest AQI: {context['lowest_aqi']['value']} at {context['lowest_aqi']['station']}" + "\033[0m")
            else:
                context['highest_aqi'] = {'value': 'N/A', 'station': 'N/A'}
                context['lowest_aqi'] = {'value': 'N/A', 'station': 'N/A'}

        if self.request.user.is_authenticated:
            favorites = Favorite.objects.filter(user=self.request.user)
            
            # Subquery to get the latest 7 distinct days for each station
            latest_days = AirQualityData.objects.filter(
                uid=OuterRef('uid')
            ).annotate(
                day=TruncDay('station_time')
            ).values('day').distinct().order_by('-day')[:7]

            # Main query to get the latest reading for each of the 7 days for each favorite station
            data = AirQualityData.objects.filter(
                uid__in=[fav.station_uid for fav in favorites]
            ).annotate(
                day=TruncDay('station_time')
            ).filter(
                day__in=Subquery(latest_days)
            ).order_by('uid', '-station_time')

            # Process the data for the context
            processed_data = {}
            for item in data:
                if item.uid not in processed_data:
                    processed_data[item.uid] = []
                if len(processed_data[item.uid]) < 7:
                    processed_data[item.uid].append({
                        'aqi': item.aqi,
                        'timestamp': item.station_time.isoformat(),
                        'station': item.station_name,
                        'uid': item.uid
                    })

            context["data"] = processed_data
            print("\033[92m" + "Processed Data:" + "\033[0m")
            print(processed_data)

        return context

#Map iframe view
class MapView(TemplateView):
    template_name = 'main/map_iframe.html'    


    @with_ip_geolocation
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        geolocation = getattr(self.request, 'geolocation', None)
        if geolocation and 'latitude' in geolocation and 'longitude' in geolocation:
            location = [geolocation['latitude'], geolocation['longitude']]
            print(location)
        else:
            location = [53.1424, -7.6921]
        figure = folium.Figure()

        
        # Make the map
        map = folium.Map(location=location, zoom_start=7, tiles='openstreetmap')

        map.add_to(figure)
        
        if self.request.user.is_authenticated:
            favorites=Favorite.objects.filter(user=self.request.user)
            # Fetch air quality data and add to map
            fetch_air_quality_data(map, favorites)
        # Fetch air quality data and add to map
        else:
            # Fetch air quality data and add to map
            fetch_air_quality_data_non_auth(map)
      
        # Render and send to template
        figure.render()
        return {"map": figure}
    
####Favorite locations
@login_required
@require_GET
def is_favorite(request, uid):
    is_fav = Favorite.objects.filter(user=request.user, station_uid=uid).exists()
    return JsonResponse({'is_favorite': is_fav})

@login_required
@require_POST
def toggle_favorite(request, uid):
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        station_uid=uid
    )
    
    if not created:
        favorite.delete()
        is_fav = False
    else:
        is_fav = True
    
    return JsonResponse({'is_favorite': is_fav})


class MedicalView(LoginRequiredMixin, TemplateView):
    template_name = 'main/medical.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Get user's medical conditions
        user_conditions = MedicalCondition.objects.filter(user=user)

        # Check if user has any conditions
        context['no_condition'] = not user_conditions.exists()

        # Get all possible conditions
        all_conditions = dict(MedicalCondition.CONDITION_CHOICES)

        # Prepare conditions data for the template
        conditions_data = []
        for condition_code, condition_name in all_conditions.items():
            condition_data = {
                'code': condition_code,
                'name': condition_name,
                'is_tracked': user_conditions.filter(condition=condition_code).exists(),
                'image': f'main/media/{condition_code.lower()}.png',
            }
            conditions_data.append(condition_data)

        context['conditions'] = conditions_data

        # Get the average rating for each condition for the last day, week, and all time
        user_conditions_data = []
        for condition in user_conditions:
            condition_data = {
                'code': condition.condition,
                'name': all_conditions[condition.condition],
                'daily_rating': self.get_average_rating(user, condition, days=1),
                'weekly_rating': self.get_average_rating(user, condition, days=7),
                'all_time_rating': self.get_average_rating(user, condition)
            }
            user_conditions_data.append(condition_data)

        context['user_conditions'] = user_conditions_data

        return context

    def get_average_rating(self, user, condition, days=None):
        query = DailyConditionRating.objects.filter(user=user, medical_condition=condition)
        if days:
            query = query.filter(date__gte=datetime.datetime.now().date() - datetime.timedelta(days=days))
        avg_rating = query.aggregate(avg_rating=Avg('rating'))['avg_rating']
        return round(avg_rating, 1) if avg_rating else None
    


@login_required
@require_POST
def add_medical_condition(request, condition_code):
    user = request.user
    
    # Use the condition_code from the URL parameter instead of POST data
    if condition_code in dict(MedicalCondition.CONDITION_CHOICES):

        if user.medicalcondition_set.filter(condition=condition_code).exists():

            messages.error(request, 'You are already tracking this condition')
            return JsonResponse({'error': 'User is already tracking this condition'}, status=400)
        else:
            MedicalCondition.objects.create(user=user, condition=condition_code)
            messages.success(request, 'Condition added successfully')
            return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'No condition code provided'}, status=400)
    
@login_required
@require_POST
def delete_medical_condition(request, condition_code):
    user = request.user
    if condition_code in dict(MedicalCondition.CONDITION_CHOICES):
        condition = user.medicalcondition_set.filter(condition=condition_code).exists()
        if condition:
            user.medicalcondition_set.filter(condition=condition_code).delete()
            messages.success(request, 'Condition deleted successfully')
            return JsonResponse({'success': True})
    else:
        return JsonResponse({'error': 'No condition code provided'}, status=400)

@login_required
@require_POST
def add_daily_condition_rating(request, condition_code, rating):
    user = request.user
    
    if condition_code in dict(MedicalCondition.CONDITION_CHOICES):
        condition = user.medicalcondition_set.filter(condition=condition_code).first()
        if condition:
            date = datetime.datetime.now()
            rating = int(rating)
            if -1 <= rating <= 11:
                DailyConditionRating.objects.update_or_create(
                    user=user,
                    medical_condition=condition,
                    date=date,
                    defaults={'rating': rating}
                )
                messages.success(request, 'Rating added successfully')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Rating must be between 0 and 10'}, status=400)
        else:
            return JsonResponse({'error': 'User is not tracking this condition'}, status=400)
    else:
        return JsonResponse({'error': f'Condition code {condition_code} does not exist. It should be one of these choices: {dict(MedicalCondition.CONDITION_CHOICES)}'}, status=400)




