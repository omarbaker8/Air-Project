from django.utils import timezone
from datetime import timedelta
from .models import APIResponse, Favorite, save_air_quality_data
import requests
import folium
from folium.plugins import HeatMap
import branca



def fetch_air_quality_data(map, favorites=None):

    try:
        # Check for the last successful API call
        last_successful_call = APIResponse.objects.filter(status='ok').order_by('-timestamp').first()
        
        if last_successful_call and (timezone.now() - last_successful_call.timestamp) < timedelta(hours=1):
            # Use data from the database
            processed_data = []
            for item in last_successful_call.air_quality_data.all():
                try:
                    aqi = int(item.aqi)
                    processed_data.append({
                        'lat': item.lat,
                        'lon': item.lon,
                        'aqi': aqi,
                        'station': item.station_name,
                        'uid': item.uid 
                    })
                except ValueError:
                    continue  # Skip items with non-numeric AQI
        else:
            # Make a new API call
            api_token = '74d142a061ee4b7631341b9bd8e1e7150800cc1b'  # Replace with your actual token
            response = requests.get(f'https://api.waqi.info/map/bounds/?token={api_token}&latlng=51.4,-10.5,55.4,-5.4')
            data = response.json()

            # Save the data to the database
            api_response = save_air_quality_data(data)

            if api_response is None:
                return 'Error saving data'

            # Process data
            processed_data = []
            for item in data['data']:
                try:
                    aqi = int(item['aqi'])
                    processed_data.append({
                        'lat': item['lat'],
                        'lon': item['lon'],
                        'aqi': aqi,
                        'station': item['station']['name'],
                        'uid': item['uid']
                    })
                except ValueError:
                    continue  # Skip items with non-numeric AQI

        # Create markers and add to map
        for item in processed_data:
            if favorites and item['uid'] in [fav.station_uid for fav in favorites]:
                html = f"""
                    <div style="font-family: Arial, sans-serif; padding: 10px;">
                        <p>
                            <strong>Station:</strong> {item['station']}<br>
                            <strong>AQI:</strong> {item['aqi']}<br>
                        </p>
                        <p>
                            <a href="#" class="station-{item['uid']}" style="text-decoration: none; color: #333; display: flex; align-items: center;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="red" stroke="red" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                </svg>
                                Remove
                            </a>
                        </p>
                    </div>
                    <script>
                        document.querySelector('.station-{item['uid']}').addEventListener('click', function(e) {{
                            e.preventDefault();
                            console.log('Clicked on station {item['uid']}');
                            window.top.postMessage({{
                                type: 'toggleFavorite',
                                uid: '{item['uid']}'
                            }}, '*');
                        }});
                    </script>
                """
            else:
                html = f"""
                    <div style="font-family: Arial, sans-serif; padding: 10px;">
                        <p>
                            <strong>Station:</strong> {item['station']}<br>
                            <strong>AQI:</strong> {item['aqi']}<br>
                        </p>
                        <p>
                            <a href="#" class="station-{item['uid']}" style="text-decoration: none; color: #333; display: flex; align-items: center;">
                                <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                </svg>
                                Add
                            </a>
                        </p>
                    </div>
                    <script>
                        document.querySelector('.station-{item['uid']}').addEventListener('click', function(e) {{
                            e.preventDefault();
                            console.log('Clicked on station {item['uid']}');
                            window.top.postMessage({{
                                type: 'toggleFavorite',
                                uid: '{item['uid']}'
                            }}, '*');
                        }});
                    </script>
                """
            iframe = branca.element.IFrame(html=html, width=200, height=200)
            folium.CircleMarker(
                location=[item['lat'], item['lon']],
                radius=get_factor(item['aqi']),
                stroke=False,
                fill=True,
                fill_color=get_color(item['aqi']),
                fill_opacity=0.2,
                popup=folium.Popup(iframe, max_width=500)
            ).add_to(map)


        # Add heatmap layer
        heat_data = [[item['lat'], item['lon'], heat_map_factor(item['aqi'])] for item in processed_data]
        HeatMap(heat_data, gradient={0.89: '#2a9d8f', 0.90: '#FFA10A', .95: '#c1121f'}).add_to(map)

        return 'Data fetched and map updated successfully'

    except Exception as e:
        return f'Error fetching or processing data: {str(e)}'
    
def fetch_air_quality_data_non_auth(map):

    try:
        # Check for the last successful API call
        last_successful_call = APIResponse.objects.filter(status='ok').order_by('-timestamp').first()
        
        if last_successful_call and (timezone.now() - last_successful_call.timestamp) < timedelta(hours=1):
            # Use data from the database
            processed_data = []
            for item in last_successful_call.air_quality_data.all():
                try:
                    aqi = int(item.aqi)
                    processed_data.append({
                        'lat': item.lat,
                        'lon': item.lon,
                        'aqi': aqi,
                        'station': item.station_name,
                        'uid': item.uid 
                    })
                except ValueError:
                    continue  # Skip items with non-numeric AQI
        else:
            # Make a new API call
            api_token = '74d142a061ee4b7631341b9bd8e1e7150800cc1b'  # Replace with your actual token
            response = requests.get(f'https://api.waqi.info/map/bounds/?token={api_token}&latlng=51.4,-10.5,55.4,-5.4')
            data = response.json()

            # Save the data to the database
            api_response = save_air_quality_data(data)

            if api_response is None:
                return 'Error saving data'

            # Process data
            processed_data = []
            for item in data['data']:
                try:
                    aqi = int(item['aqi'])
                    processed_data.append({
                        'lat': item['lat'],
                        'lon': item['lon'],
                        'aqi': aqi,
                        'station': item['station']['name'],
                        'uid': item['uid']
                    })
                except ValueError:
                    continue  # Skip items with non-numeric AQI

        # Create markers and add to map
        for item in processed_data:

            html = f"""
                <div style="font-family: Arial, sans-serif; padding: 10px;">
                    <p>
                        <strong>Station:</strong> {item['station']}<br>
                        <strong>AQI:</strong> {item['aqi']}<br>
                    </p>
                </div>
            """
            iframe = branca.element.IFrame(html=html, width=200, height=200)
            folium.CircleMarker(
                location=[item['lat'], item['lon']],
                radius=get_factor(item['aqi']),
                stroke=False,
                fill=True,
                fill_color=get_color(item['aqi']),
                fill_opacity=0.2,
                popup=folium.Popup(iframe, max_width=500)
            ).add_to(map)


        # Add heatmap layer
        heat_data = [[item['lat'], item['lon'], heat_map_factor(item['aqi'])] for item in processed_data]
        HeatMap(heat_data, gradient={0.89: '#2a9d8f', 0.90: '#FFA10A', .95: '#c1121f'}).add_to(map)

        return 'Data fetched and map updated successfully'

    except Exception as e:
        return f'Error fetching or processing data: {str(e)}'
        
def get_color(aqi):
    if aqi <= 20:
        return '#2a9d8f'
    elif aqi <= 30:
        return 'yellow'
    elif aqi <= 50:
        return 'orange'
    elif aqi <= 200:
        return 'red'
    elif aqi <= 300:
        return 'purple'
    else:
        return 'maroon'
    
def get_factor(input):
    
        return input * 1.2

def heat_map_factor(input):
    return input * 10