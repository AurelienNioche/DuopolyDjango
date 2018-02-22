from django.test import TestCase

# Create your tests here.
from django.test import Client
c = Client()

args = dict()

args["demand"] = "ask_to_register"
args["email"] = "nioche.aurelien@gmail.com"
args["gender"] = "male"
args["nationality"] = "french"
args["mechanical_id"] = "Tonpere"
args["age"] = 31

response = c.post('/register/', args)
print(response.status_code)
# response = c.get('/consumer/details/')
print("response: ", response.content)
