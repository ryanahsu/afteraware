from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Your Twilio account information
account_sid = 'AC279b93ebe0524bc08ab1791d3d29da4b'
auth_token = 'b6834fe26655e01e8393a9a56e98a574'
twilio_phone_number = '+15074185220'

# Create a Twilio client
client = Client(account_sid, auth_token)

# Start a Flask app
app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def sms_reply():
    # Extract the message
    msg = request.form.get('Body')

    # Send a reply
    resp = MessagingResponse()
    resp.message("You said: " + msg)

    return str(resp)

if __name__ == '__main__':
    # Start the Flask app
    app.run(debug=True)
