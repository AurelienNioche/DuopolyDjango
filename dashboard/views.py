from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.gzip import gzip_page
from django.db import transaction
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import os

from . forms import RoomForm
from utils import utils

from parameters import parameters

import game.room.dashboard
import game.user.dashboard


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
            utils.log("Logging {} user.".format(user), f=login)
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
                    # Create room
                    game.room.dashboard.create(form.get_data())

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

        # check connected users
        game.user.dashboard.check_connected_users()

        # Get list of existing rooms and players
        rooms_list = game.room.dashboard.get_list()

        context.update({"rooms": rooms_list})

        return context

    def post(self, request, *args, **kwargs):

        if "delete" in request.POST:
            room_id = request.POST["delete"]
            utils.log("Delete room {}.".format(room_id), f=self.post)

            # Delete room
            game.room.dashboard.delete(room_id=room_id)

        return redirect("/room_management")


@method_decorator(login_required, name='dispatch')
class DataView(TemplateView):
    template_name = "components/data.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        # Get list of existing rooms
        url_pickle = game.room.dashboard.convert_data_to_pickle()
        url_sql = game.room.dashboard.convert_data_to_sql()

        context.update({"subtitle": "Download data"})
        context.update({"url_pickle": url_pickle})
        context.update({"url_sql": url_sql})

        return context


@method_decorator(gzip_page, name='dispatch')
@method_decorator(login_required, name='dispatch')
class LogsView(TemplateView):
    template_name = "components/logs.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context.update({"subtitle": "Logs"})

        if os.path.exists(parameters.logs_path):
            files = sorted(
                [f for f in os.listdir(parameters.logs_path)
                 if os.path.isfile("".join([parameters.logs_path, f]))]
            )
        else:
            files = []

        current_file = files[-1]
        context.update({"current_file": current_file})
        context.update({"logs": self.refresh_logs(current_file)})
        context.update({"files": files})

        return context

    def dispatch(self, request, *args, **kwargs):

        if "refresh_logs" in request.GET:
            if request.GET["refresh_logs"]:

                filename = request.GET["filename"]
                n_lines = int(request.GET["n_lines"])

                return JsonResponse(
                    {
                        "logs": self.refresh_logs(filename, n_lines)
                     }
                )

        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def refresh_logs(filename, n_lines=None):

        f = parameters.logs_path + filename
        if os.path.exists(f):
            with open(parameters.logs_path + filename, "r") as f:
                # if n_lines:
                logs = "".join(f.readlines()[-500:])
                # else:
                #     logs = f.read()
            return logs
