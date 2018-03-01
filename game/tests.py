from django.test import TestCase

# Create your tests here.
from django.test import Client

import numpy as np
from django_bulk_update.helper import bulk_update

from game.models import ConsumerChoice

print("ta mere")

# c = Client()
#
# args = dict()
#
# args["demand"] = "ask_to_register"
# args["email"] = "nioche.aurelien@gmail.com"
# args["gender"] = "male"
# args["nationality"] = "french"
# args["mechanical_id"] = "Tonpere"
# args["age"] = 31
#
# response = c.post('/register/', args)
# print(response.status_code)
# # response = c.get('/consumer/details/')
# print("response: ", response.content)


consumers = [i[0] for i in ConsumerChoice.objects.values_list('value').filter(round_id=96, t=0).order_by("agent_id")]
print(consumers)

# for agent_id, c in enumerate(consumers):
#
#     print("tamere", agent_id)
#
#     choice = np.random.randint(13)
#
#     # Save choice
#     c.value = choice
#
#
# bulk_update(consumers, update_fields=['value'])