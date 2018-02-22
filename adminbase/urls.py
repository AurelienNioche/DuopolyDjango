from django.conf.urls import include, url
from django.contrib import admin


app_name = "adminbase"
urlpatterns = [
    url(r'^', include('dashboard.urls', namespace='dashboard')),
    url(r'^', include('game.urls', namespace='game')),
    url(r'^', include('messenger.urls', namespace='messenger')),
    url(r'^admin/', admin.site.urls),
]
