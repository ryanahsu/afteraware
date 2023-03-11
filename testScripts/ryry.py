import airtable
import datetime as dt
import time
from twilio.rest import Client


import os

# Set your Twilio account SID, authentication token, and instantiate the client
account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'bfab954301b0b78005b61d1210d661ac'
client = Client(account_sid, auth_token)

# Set your Airtable API key, Base ID, and table name
AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appFzlyJRq6XYKsIH'
AIRTABLE_TABLE_NAME = 'table 1'

while (True):
  # Create an instance of the Airtable client
  at = airtable.Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME,
                         AIRTABLE_API_KEY)
  sender_number = "+14093163562"
  message_body = "test_add"

  data = {}
  for page in at.get_iter():
    for record in page:
      data[record['fields']['Name']] = record['fields']['Values']

  key_list = data.keys()
  # print(key_list)
  # print(data)

  now = str(dt.datetime.now().strftime("%H:%M")).lstrip('0')
  print(now)
  check = True
  if (now in key_list and check == True):
    num_list = data[now].replace(" ", "").split(",")
    for num in num_list:
      message = client.messages.create(
              body='Reminding you to take your medicine now (' + now + ')!',
              to=num,
                from_='+14093163562'
      )
      print('Message sent!')
    now = 0
    check = False
