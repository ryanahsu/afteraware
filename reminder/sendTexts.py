import airtable
import datetime as dt
import time
from twilio.rest import Client
import os

# Set your Twilio account SID, authentication token, and instantiate the client
account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'b6834fe26655e01e8393a9a56e98a574'
client = Client(account_sid, auth_token)

# Set your Airtable API key, Base ID, and table name
AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appLDM3F8B89UY71p'
AIRTABLE_TABLE_NAME = 'Reminders'

# Create an instance of the Airtable client
at = airtable.Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)

while True:
    # Fetch reminder times and associated phone numbers from Airtable
    data = {}
    for page in at.get_iter():
        for record in page:
            time_string = record['fields']['Time'].lstrip('0')
            data[time_string] = record['fields']['PhoneNumbers']

    now = dt.datetime.now().strftime("%H:%M:%S").lstrip('0')

    if now in data:
        phone_numbers = data[now].split(',')

        for phone_number in phone_numbers:
            cleaned_phone_number = phone_number.strip()
            message = client.messages.create(
                body='Reminding you to take your medicine now (' + now + ')!',
                from_='+15074185220',
                to=phone_number.strip()
            )
            print(f'Message sent to {phone_number.strip()} at {now}!')

    time.sleep(1)  # Wait for 1 second before checking the time again
