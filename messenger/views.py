from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
import os

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

import game.user.messenger

from . import management

__path__ = os.path.relpath(__file__)


@method_decorator(login_required, name='dispatch')
class MessengerView(TemplateView):

    template_name = "components/messenger.html"
    user = None

    def get_context_data(self, **kwargs):

        """
        Last method to be called.
        Updates the context
        with current info.
        """

        context = super().get_context_data(**kwargs)

        # Set titles of the page
        context.update({'subtitle': "Chat with players"})

        # Update connected players
        game.user.messenger.check_connected_users()

        # Get messages
        users = management.get_all_users()
        # update context with users
        context.update({"users": users})
        # Get slide auto_reply value
        auto_reply = management.get_auto_reply()
        # update context with auto_reply
        context.update({"auto_reply": auto_reply})

        # get current user if a user is selected
        if self.user is not None:

            management.set_user_msg_as_read(self.user)

            context.update(
                {"current_user": self.user}
            )

        else:
            user = management.get_latest_msg_author().username
            management.set_user_msg_as_read(user)
            context.update(
                {"current_user": user}
            )

        # update context with messages
        messages = management.get_all_messages_from_user(context['current_user'])

        # reload = any(not m.receipt_confirmation for m in messages)
        context.update({'messages': messages})
        # context.update({'reload': reload})

        return context

    def dispatch(self, request, *args, **kwargs):

        """
        Dispatch is the first method to be called.
        After checking the url for a user selected, and
        checking the post data (to see if a msg is submitted)
        let the TemplateView do its stuff (get_context_data...)
        """

        if "user_id" in request.GET:

            user_id = request.GET["user_id"]

            if user_id != "null":
                self.user = management.get_user_from_id(user_id)
        else:
            user_id = management.get_latest_msg_author().id
            return redirect('/messenger_view/?user_id={}'.format(user_id))

        # If it is an "auto_reply" setting request
        if "auto_reply" in request.GET:
            raise Exception("Tamere")
            management.set_auto_reply(int(request.GET["auto_reply"]))

        # There are different type of refresh request
        # msg -> refresh all msg from the select user
        # contacts -> refresh contact list
        # all_unread_msg -> refresh the new msg counter (located on the sidebar)
        if "type" in request.GET:

            if request.GET["type"] == "msg":
                return self.refresh_msg(request, **kwargs)

            elif request.GET["type"] == "contacts":
                return self.refresh_contacts(request, **kwargs)

            elif request.GET["type"] == "all_unread_msg":
                return self.refresh_all_unread_msg(request, **kwargs)

        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        """
        used when sending a msg
        """
        username = request.POST["user"]
        management.send_message(username=username, message=request.POST["msg"])

        return HttpResponse("Sent!")

    def refresh_msg(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, MessengerRefreshView.msg_template_name, context)

    @staticmethod
    def refresh_all_unread_msg(request, **kwargs):
        return JsonResponse({"count": management.get_unread_msg()})

    def refresh_contacts(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, MessengerRefreshView.contact_template_name, context)


class MessengerRefreshView(TemplateView):
    msg_template_name = "components/msg_refresh.html"
    contact_template_name = "components/contact_refresh.html"


class MessengerClientSide:

    @classmethod
    @csrf_exempt
    def messenger(cls, request):
        demand = request.POST["demand"]

        # retrieve method
        command = getattr(cls, demand)

        to_reply = "/".join((str(i) for i in command(request)))

        response = HttpResponse(to_reply)
        response["Access-Control-Allow-Credentials"] = "true"
        response["Access-Control-Allow-Headers"] = "Accept, X-Access-Token, X-Application-Name, X-Request-Sent-Time"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Origin"] = "*"
        return response

        # ----------- Demand relatives to messenger --------------- #

    @classmethod
    def client_speaks(cls, request):

        username = request.POST["username"].lower()
        message = request.POST["message"]

        management.new_message_from_client(username=username, message=message)

        return "reply", "done"

    @classmethod
    def client_hears(cls, request):

        username = request.POST["username"].lower()

        n_new_messages, new_messages = management.get_messages_for_client(username=username)

        return ("reply", n_new_messages,) + tuple((i for i in new_messages))

    @classmethod
    def client_receipt_confirmation(cls, request):

        username = request.POST["username"].lower()
        messages_list = request.POST["message"]
        messages = [i for i in messages_list.split("/") if len(i)]

        management.receipt_confirmation_from_client(username, messages)

        return "reply", "done."
