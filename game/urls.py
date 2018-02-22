from django.conf.urls import url
from . import views


app_name = "game"
urlpatterns = [
    url(r'^client_request/$', views.client_request),
]
