from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from utils import utils

import game.views


class GameWebSocketConsumer(JsonWebsocketConsumer):

    def connect(self):

        self.accept()

    def disconnect(self, close_code):

        utils.log(f'Disconnection! close code: {close_code}', f=self.disconnect)
        # self._group_discard('all')

    def receive_json(self, content, **kwargs):

        # If demand is a ping,
        # reply pong then exit the method
        if content.get('demand') == 'ping':

            self.send('pong')
            return

        to_reply = game.views.client_request(content)

        if to_reply:

            self.send_json(to_reply)

            try:
                utils.log(f'Sending to current channel: {to_reply}', f=self.receive_json)
            except UnicodeEncodeError:
                print('Error printing request.')

    # def _group_management(self, consumer_info):
    #
    #     """
    #     Adding current connected user to group
    #     :param consumer_info:
    #     :return:
    #     """
    #
    #     player_id = consumer_info.get('player_id')
    #     username = consumer_info.get('username')
    #
    #     demand_func = \
    #         getattr(game.views, demand) if isinstance(demand, str) else None
    #
    #     if user_id:
    #
    #         # if user_id is available
    #         # add the corresponding group
    #         # Each user_id group matches only
    #         # user/client/device
    #         id_group = f'user-{user_id}'
    #         utils.log(f'Adding group {id_group}', f=self._group_management)
    #         self._group_add(group=id_group)
    #
    #     if demand_func == game.views.choice:
    #
    #         t = consumer_info.get('t')
    #
    #         # Add user to the current t group
    #         game_group_t = f'game-t-{t}'
    #         self._group_add(game_group_t)
    #
    #         # Discard user from group t - 1
    #         game_group_t_minus_1 = f'game-t-{t-1}'
    #         self._group_discard(game_group_t_minus_1)
    #
    #         # If user calls the choice method it means that
    #         # training is done
    #         # So that we remove him from that
    #         # group too
    #         training_group_discard = 'training-done'
    #         self._group_discard(training_group_discard)
    #
    #     elif demand_func == game.views.training_done:
    #
    #         # If training_done is called add user to the
    #         # corresponding group
    #         training_group_add = 'training-done'
    #         self._group_add(training_group_add)
    #
    #     # Remove user from all other groups
    #     for group in demand_state_mapping.keys():
    #         self._group_discard(group=group)
    #
    #     if state:
    #         self._group_add(group=state)

    # def group_message(self, message):
    #
    #     """
    #     Send json to a group, called by self._group_send
    #     method and WSDialog.group_send from outside
    #     :param message:
    #     :return:
    #     """
    #
    #     data = message['data']
    #     group = message['group']
    #     is_json = message['json']
    #
    #     if is_json:
    #         try:
    #             utils.log(f'Sending to group {group}: {data}', f=self._group_send)
    #         except UnicodeEncodeError:
    #             print('Error printing request.')
    #
    #         self.send_json(data)
    #     else:
    #         self.send(data)
    #
    # def start_pinging(self):
    #
    #     async_to_sync(self.channel_layer.send)(
    #         'ping-consumer',
    #         {
    #             'type': 'ping'
    #         },
    #     )
    #
    # def _send_to_worker(self, demand, data):
    #
    #     async_to_sync(self.channel_layer.send)(
    #         'receipt-consumer',
    #         {
    #             'type': 'generic',
    #             'demand': demand,
    #             'receipt_data': data
    #         },
    #     )
    #
    # def _group_send(self, group, data, json=True):
    #
    #     """
    #     Send data to a desired group of users
    #     :param group:
    #     :param data:
    #     :return:
    #     """
    #
    #     async_to_sync(self.channel_layer.group_send)(
    #         group,
    #         {
    #             'type': 'group.message',
    #             'data': data,
    #             'group': group,
    #             'json': json
    #          }
    #     )
    #
    # def _group_add(self, group):
    #
    #     """
    #     add a user to a group
    #     :param group:
    #     """
    #     async_to_sync(self.channel_layer.group_add)(
    #         group,
    #         self.channel_name
    #     )
    #
    # def _group_discard(self, group):
    #
    #     """
    #     remove a user from a group
    #     :param group:
    #     """
    #     async_to_sync(self.channel_layer.group_discard)(
    #         group,
    #         self.channel_name
    #     )

