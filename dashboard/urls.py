from django.conf.urls import url
from . import views


app_name = "dashboard"
urlpatterns = [
    url(r'^$', views.LoginView.as_view(), name="login"),
    url(r'^login$', views.LoginView.login, name="login"),
    url(r'^logout$', views.LoginView.logout, name="login"),
    url(r'^room_management/$', views.RoomManagementView.as_view(), name='room_management'),
    url(r'^new_room/$', views.NewRoomView.as_view(), name="new_room"),
    url(r'^data/$', views.DataView.as_view(), name="data"),
    url(r'^logs/$', views.LogsView.as_view(), name="logs"),
]
