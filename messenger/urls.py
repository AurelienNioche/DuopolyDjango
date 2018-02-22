from django.conf.urls import url
from . import views


app_name = "messenger"
urlpatterns = [
    url(r'^messenger/$', views.MessengerClientSide.messenger),
    url(r'^messenger_view/$', views.MessengerView.as_view(), name='messenger_view'),
    url(r'^refresh_messenger/$', views.MessengerView.as_view())
]
