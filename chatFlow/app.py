from flask import Flask, request, jsonify
import requests
import airtable
import json
import os
from twilio.rest import Client
import openai
import json



os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/aryanmahindra/Downloads/innate-summit-378204-849ac63c3e24.json'

app = Flask(__name__)

# Airtable info
AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appFzlyJRq6XYKsIH'
AIRTABLE_TABLE_NAME = 'table 1'






image_url = 'https://drive.google.com/uc?id=1Vv8cGKMl0oBgOq3sLuszr19eaYkbxAT5'

# Twilio info
account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'bfab954301b0b78005b61d1210d661ac'
from_='+14093163562'
patient_val = ""

# OpenAI info
openai.api_key = "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"

# Route for handling incoming messages

numbers_list = None

# Set up the message content and recipient phone number
message_body = 'Hi, thanks for signing up to AfterAware!'
message_body_1 = "Simply reply back with the time syou want to be reminded :)\nReply with multiple times in a list '21:34, 9:00, 18:00'\n Or a single time like '9:00' \n\n Image example inbound:) \n\n\n       ↓↓↓↓↓↓↓↓↓↓↓"
message_body_2 = "Invalid entry! Remember to list your times such as 11:00 or 11:00, 21:00"
message_body_3 = "You are all set! Will remind you soon :)"
client = Client(account_sid, auth_token)
patient_number = None
convoStarted = False

@app.route('/conversation', methods=['POST'])
def start_conversation():
    print("chatFlow started")
    patient_number = request.values.get('Number', None)
    patient_number = "+1"+patient_number.strip()
    patient_number.strip()
    patient_val = ""+patient_number



    print(patient_number)

    client = Client(account_sid, auth_token)



    from_='+14093163562'

    # Send the message
    message1 = client.messages.create(
        body='Hi, thanks for signing up to AfterAware!',
        from_='+14093163562',  # Your Twilio phone number here
        to=patient_number
    )

    message = client.messages.create(
        body=message_body_1,
        from_='+14093163562',  # Your Twilio phone number here
        to=patient_number
    )

    message = client.messages.create(
        to=patient_number,
        from_='+14093163562',
        body="↑↑↑↑↑↑↑↑↑↑↑\n\n Make sure to reply back with 'DONE' to start the service!",
        media_url=[image_url]
    )





    # Get the message body and sender's phone number

    # Print the message SID to confirm that the message was sent
    print('Message SID:', message.sid)
    checker = ""
    numbers_list = None
    #while (checker.casefold() != "done") :
    while True:

        client = Client(account_sid, auth_token)
        reply_messages = client.messages.list(to=from_, from_=patient_val)
        reply_messages = client.messages.list(to=from_, from_=patient_val)
        if reply_messages:
            most_recent_message = reply_messages[0]
            checker = most_recent_message.body
        else:
            # Handle the case where the list is empty

            most_recent_message = message1  # Or set a default value or raise an exception, depending on your requirements



        if "done" in checker.lower() or "DONE" in checker or "Done" in checker:
            break
        else :
            #get all the values from this and store it in a list
            print("values here ->>>>>  "+most_recent_message.body)
            numbers_list = most_recent_message.body.split(", ")

            if any(word.isalpha() for word in most_recent_message.body.split()):

                print("The entry is not valid")


            else:
                print("The entry is valid")






    print("exited chatFlow and here are the times for -> "+patient_number)
    airtable_client = airtable.Airtable(
        AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)
    if(numbers_list != None):
        for item in numbers_list:

            print(item)

            entry = airtable_client.search('Name', item)

            if (len(entry) == 0):
                print("new entry")
                airtable_client.insert({
                    'Name': item,
                    'Values': patient_number})


            elif 'Values' in entry[0]['fields']:
                print("entry has to be updated")
                currentStatus = entry[0]['fields']["Values"]
                airtable_client.update(
                    entry[0]['id'], {'Values': patient_number + ", A: " + patient_number}, typecast=True)




        message = client.messages.create(
            body=message_body_3,
            from_='+14093163562',  # Your Twilio phone number here
            to=patient_number
        )








    return jsonify("success")




if __name__ == 'main':
    # Start ngrok

    ngrok_url = 'http://localhost:4040/api/tunnels'
    response = requests.get(ngrok_url)
    data = response.json()
    ngrok_tunnel = data['tunnels'][0]['public_url']
    #print('ngrok tunnel:', ngrok_tunnel)

    # Set up the Twilio webhook URL
    twilio_url = ngrok_tunnel + '/sms'
    #print('Twilio URL:', twilio_url)

    # Run the Flask app
    app.run(debug=True)