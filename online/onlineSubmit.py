from datetime import datetime
import airtable
import requests
from flask import Flask, jsonify, render_template, request
from twilio.rest import Client

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

    records = airtable_signups.search('Phone Number', phone)
    if records:
        # A record with the same phone number already exists
        # Return an error message to the user
        return "Phone number already exists"
    else:
        airtable_signups.insert({
            'Phone Number': phone,
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


@app.route("/checkin", methods=["GET"])
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
    # Get patient phone number to text
    patient_number = request.values.get('number', None)

    # Get the current time
    now = datetime.now()
    formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")

    if isinstance(airtable_conversations, airtable.Airtable):
        print('Airtable object is valid')
    else:
        print('Airtable object is not valid')

    '''
    airtable_conversations.insert({
        'Time': formatted_date_time,
        'Sender': '+14093163562',
        'Receiver': patient_number,
        'Text': 'HELLOOOOOO'})
    '''


    '''
    openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant",
                "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": "Where was it played?"}
        ]
    )
    '''


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)
