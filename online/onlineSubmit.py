import airtable
import requests
from flask import Flask, render_template, request
from twilio.rest import Client

app = Flask(__name__)

AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appLDM3F8B89UY71p'
AIRTABLE_TABLE_NAME = 'table 1'
airtable_client = airtable.Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)

account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'b6834fe26655e01e8393a9a56e98a574'

client = Client(account_sid, auth_token)


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

    records = airtable_client.search('Phone Number', phone)
    if records:
        # A record with the same phone number already exists
        # Return an error message to the user
        return "Phone number already exists"
    else:
        airtable_client.insert({
            'Phone Number': phone,
            'Clinic': clinic,
            'Condition': text,
            'Reminder': reminder,
            'Times': times_string
        })
        # Send a POST request to the success URL

        message = client.messages.create(
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



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
