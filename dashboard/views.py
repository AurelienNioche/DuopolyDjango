from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.utils import IntegrityError
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import os

from .forms import RoomForm
from utils import utils

from game import room, round as rd
from parameters import parameters

__path__ = os.path.relpath(__file__)


class LoginView(TemplateView):

    template_name = "components/login.html"

    def get_context_data(self, **kwargs):

        context = super(LoginView, self).get_context_data(**kwargs)

        return context

    @classmethod
    def login(cls, request):

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user is not None:
            utils.log("Logging {} user.".format(user), f=utils.function_name(), path=__path__)
            login(request, user)
            return redirect("/room_management/")

        else:
            return render(request, cls.template_name, {"fail": 1})

    @classmethod
    def logout(cls, request):

        logout(request)
        return redirect("/")


@method_decorator(login_required, name='dispatch')
class NewRoomView(TemplateView):

    template_name = "components/new_room.html"

    def get_context_data(self, **kwargs):

        context = super(NewRoomView, self).get_context_data(**kwargs)
        context.update({"subtitle": "Set parameters and create a room"})
        form = RoomForm()

        context.update({'form': form})

        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        """
        Room creation process
        :param request: using POST request
        :return: html room form template (success or fail)
        """

        if request.POST["form_function"] == "room_organisation":

            form = RoomForm(request.POST)

            if form.is_valid():

                with transaction.atomic():
                    try:
                        # Create room
                        room.dashboard.create(form.get_data())
                    except IntegrityError:
                        utils.log("Room already exists!", f=utils.function_name(), path=__path__, level=2)

                return redirect("/room_management")

            else:
                context = {"subtitle": "Set parameters and create a room", "form": form}
                return render(request, self.template_name, context)

        else:
            raise Exception("Error validating the form.")


@method_decorator(login_required, name='dispatch')
class RoomManagementView(TemplateView):

    template_name = "components/room_management.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context.update({'subtitle': "Room list"})

        # Get list of existing rooms
        rooms_list = room.dashboard.get_list()

        context.update({"rooms": rooms_list})

        return context

    def post(self, request, *args, **kwargs):

        if "delete" in request.POST:
            room_id = request.POST["delete"]
            utils.log("Delete room {}.".format(room_id), f=utils.function_name(), path=__path__)

            # Delete room
            room.dashboard.delete(room_id=room_id)

        return redirect("/room_management")


@method_decorator(login_required, name='dispatch')
class DataView(TemplateView):
    template_name = "components/data.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # Get list of existing rooms
        url = rd.dashboard.convert_data_to_pickle()

        context.update({"subtitle": "Download data"})
        context.update({"url": url})

        return context


@method_decorator(login_required, name='dispatch')
class LogsView(TemplateView):
    template_name = "components/logs.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({"subtitle": "Logs"})
        context.update({"logs": self.refresh_logs()})

        return context

    def dispatch(self, request, *args, **kwargs):

        if "refresh_logs" in request.GET:
            if request.GET["refresh_logs"]:
                return JsonResponse({"logs": self.refresh_logs()})

        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def refresh_logs():

        with open(parameters.logs_path, "r") as f:
            logs = f.read()
            f.close()
        return logs

