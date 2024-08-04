from django.urls import path
from .import views
from .views import HomeView, MapView , MedicalView 

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('api/add_daily_condition_rating/<str:condition_code>/<int:rating>/', views.add_daily_condition_rating, name='add_daily_condition_rating'),
    path('api/add_medical_condition/<str:condition_code>/', views.add_medical_condition, name='add_medical_condition'),
    path('api/delete_medical_condition/<str:condition_code>/', views.delete_medical_condition, name='delete_medical_condition'),
    path('api/is_favorite/<int:uid>/', views.is_favorite, name='is_favorite'),
    path('api/toggle_favorite/<int:uid>/', views.toggle_favorite, name='toggle_favorite'),
    path('map_iframe/', MapView.as_view(), name='map_iframe'),
    path('medical/', MedicalView.as_view(), name='medical')
]