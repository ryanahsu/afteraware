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
airtable_conversations = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Conversations', AIRTABLE_API_KEY)

account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'b6834fe26655e01e8393a9a56e98a574'

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
            'Times': times_string
        })
        # Send a POST request to the success URL

        message = twilio.messages.create(
            to=phone,
            from_='+14093163562',
            body='Welcome to AfterAware!'
        )
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


@app.route("/checkin", methods=["POST"])
# TODO: eventually add CORS/similar checking to protect endpoints
def checkin():
    # Get patient phone number to text
    patient_number = request.values.get('number', None)

    # Send text
    message = twilio.messages.create(
        to=patient_number,
        from_='+14093163562',
        body='Hi! This is AfterAware checking in on your health. How are you today?'
    )

    # Print the message SID to confirm that the message was sent
    print('Message SID:', message.sid)

    # Indicate success
    return jsonify("success"), 200


@app.route("/reply", methods=["POST"])
def reply():
    # Get patient and chatbot message info
    patient_number = "+" + request.values.get('patient_number', None)
    chatbot_number = "+" + request.values.get("chatbot_number", None)
    patient_message = request.values.get("message", None)

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
    conversation = airtable_conversations.search(formula=query)

    # TODO: add length of conversation checking

    # Sort the records based on the Time field
    sorted_convo = sorted(conversation, key=lambda x: datetime.strptime(
        x['fields']['Time'], '%H:%M:%S'))

    # Build text history for the day
    messages = list()
    messages.append(
        {"role": "system", "content": "You are a doctor checking in post-operation on a patient with condition {0}".format(condition)})
    for message in sorted_convo:
        if message["fields"]["Sender"] == patient_number:
            messages.append(
                {"role": "patient", "content": message["fields"]["Text"]})
        else:
            messages.append(
                {"role": "doctor", "content": message["fields"]["Text"]})

    # Generate next doctor question
    question = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    response_text = question.choices[0].text

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
        'Text': response_text})

    return jsonify("success"), 200


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
