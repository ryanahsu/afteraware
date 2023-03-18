from datetime import date, datetime
import airtable
import requests
from flask import Flask, jsonify, render_template, request
from twilio.rest import Client
import openai

app = Flask(__name__)

AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appLDM3F8B89UY71p'
airtable_signups = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Signups', AIRTABLE_API_KEY)
airtable_reminders = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Reminders', AIRTABLE_API_KEY)
airtable_conversations = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Conversations', AIRTABLE_API_KEY)

url = "https://remindersdeployeduspst.uk.r.appspot.com/checkin"

account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'b6834fe26655e01e8393a9a56e98a574'

airtable_client = airtable.Airtable(AIRTABLE_BASE_ID, 'Signups', AIRTABLE_API_KEY)

openai.api_key = "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"

twilio = Client(account_sid, auth_token)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    text = request.form.get("input-text")
    phone = request.form.get("input-phone")
    clinic = request.form.get("input-clinics")
    reminder = request.form.get("input-reminder")
    times = request.form.getlist("input-time[]")
    phone = "+1" + phone

    # Remove duplicate times
    times = list(set(times))
    times = [time + ':00' for time in times]

    print(times)
    print(phone)

    for time in times:
        # Define the search query
        search_query = f"{{Time}} = '{time}'"

        # Search for the record in the Airtable
        result = airtable_reminders.search("Time", time)

        # If the record exists, append the phone number to the PhoneNumbers field
        if result:
            record_id = result[0]['id']
            phone_numbers = result[0]['fields']['PhoneNumbers']
            if not isinstance(phone_numbers, list):
                phone_numbers = [phone_numbers]
            phone_numbers.append(phone)
            my_string = "', '".join(phone_numbers)
            airtable_reminders.update(record_id, {'PhoneNumbers': my_string})

        # If the record does not exist, create a new record with the time and phone number
        else:
            airtable_reminders.insert({'Time': time, 'PhoneNumbers': phone})

    times_string = ', '.join(times)

    records = airtable_signups.search('Patient Number', phone)
    if records:
        # A record with the same phone number already exists
        # Return an error message to the user
        return "Phone number already exists"
    else:
        airtable_signups.insert({
            'Patient Number': phone,
            'Clinic': clinic,
            'Condition': text,
            'Reminder': reminder,
            'Times': times_string,
        })
        # Send a POST request to the success URL

        message = twilio.messages.create(
            to=phone,
            from_='+15074185220',
            body="Welcome to AfterAware! How has your condition of {} changed from your last visit to the clinic?".format(text.lower())
        )
        #send_request()
        # The request to the success URL was successful
        return """
                <html>
                <head>
                    <meta http-equiv="refresh" content="5; url=/">
                    <style>
                        #animation {
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                        }
                        .checkmark {
                            width: 70px;
                            height: 70px;
                            border-radius: 50%;
                            display: inline-block;
                            stroke-width: 3px;
                            stroke: #4CAF50;
                            stroke-dasharray: 166;
                            stroke-dashoffset: 166;
                            animation: stroke-checkmark 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards;
                        }
                        @keyframes stroke-checkmark {
                            100% {
                                stroke-dashoffset: 0;
                            }
                        }
                    </style>
                </head>
                <body>
                    <div id="animation">
                        <svg class="checkmark" viewBox="0 0 52 52">
                            <circle class="checkmark__circle" cx="26" cy="26" r="25" fill="none"/>
                            <path class="checkmark__check" fill="none" d="M14.1 27.2l7.1 7.2 16.7-16.8"/>
                        </svg>
                    </div>
                </body>
                </html>
            """

    print(message.sid)


def send_request():
    patient_numbers = []
    records = airtable_client.get_all()
    for record in records:
        patient_numbers.append(record['fields']['Patient Number'])

    patient_numbers = list(set(patient_numbers))

    for patient_number in patient_numbers:
        params = {"patient_number": patient_number}
        response = requests.post(url, params=params)


@app.route("/checkin", methods=["POST"])
# TODO: eventually add CORS/similar checking to protect endpoints
def checkin():
    # Get patient phone number to text

    patient_number = "+" + request.values.get('patient_number', None)
    print(patient_number)
    # Send text
    message = twilio.messages.create(
        to=patient_number,
        from_='+15074185220',
        body='Hi! This is AfterAware checking in on your health. How are you today?'
    )

    '''

    '''

    # Print the message SID to confirm that the message was sent
    print('Message SID:', message.sid)

    # Indicate success
    return jsonify("success"), 200


@app.route("/reply", methods=["POST"])
def reply():
    # Get patient and chatbot message info
    patient_number = request.values.get('From', None)
    chatbot_number = request.values.get("To", None)
    patient_message = request.values.get("Body", None)

    if patient_number == None or chatbot_number == None or patient_message == None:
        return jsonify({'error': 'Required message information missing'}), 400

    # Get patient condition
    patient_info = airtable_signups.search('Patient Number', patient_number)
    if patient_info:
        condition = patient_info[0]['fields']['Condition']
    else:
        return jsonify({'error': 'Patient entry not found'}), 400

    # Get the current time
    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M:%S")

    # Insert message record into airtable
    airtable_conversations.insert({
        'Date': today,
        'Time': current_time,
        'Sender': patient_number,
        'Receiver': chatbot_number,
        'Text': patient_message})
    # Define the search formula
    query = "AND(Date='{0}', OR(Sender='{1}', Receiver='{2}')".format(
        today, patient_number, chatbot_number)

    # Search for records that match the formula
    # conversation = airtable_conversations.search(formula=query)

    conversation = airtable_conversations.search('Date', today, formula=query)

    # TODO: add length of conversation checking

    # Sort the records based on the Time field
    sorted_convo = sorted(conversation, key=lambda x: datetime.strptime(
        x['fields']['Time'], '%H:%M:%S'))

    print(sorted_convo)

    # Build text history for the day
    messages = list()
    messages.append(
        {"role": "system",
         "content": "You cannot give medical advice. No suggestions. Only questions. The patients condition is {0}. No medical advice. Only ask questions".format(
             condition)})
    for message in sorted_convo:
        if message["fields"]["Sender"] == patient_number:
            messages.append(
                {"role": "user", "content": message["fields"]["Text"]})
        else:
            messages.append(
                {"role": "assistant", "content": message["fields"]["Text"]})

    print("this is the message")
    print(messages)
    response_text = ""
    # Generate next doctor question


    question = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        )

    print("updated question____________")

    response_text = question.choices[0].message['content']
    print(response_text)
    print("This is the question")
    print("This is the response text")
    print(response_text)


    # Send text
    message = twilio.messages.create(
            to=patient_number,
            from_=chatbot_number,
            body=response_text
        )

    # Get the current time
    today = date.today().isoformat()
    current_time = datetime.now().strftime("%H:%M:%S")

    # Add outgoing text to airtable
    airtable_conversations.insert({
            'Date': today,
            'Time': current_time,
            'Sender': chatbot_number,
            'Receiver': patient_number,
            'Text': response_text
        })
    return jsonify("success"), 200







