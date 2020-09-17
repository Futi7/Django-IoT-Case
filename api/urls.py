from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_doc, name='index'),
    path('device-list/', views.device_list, name='devices'),
    path('device-detail/<int:id>/', views.device_detail, name='device-detail'),
    path('device-status-update/<int:id>', views.device_status_update, name='device-status-update'),
    path('device-status-percentage/<int:id>', views.device_status_percentage, name='device-status-percentage'),
]
