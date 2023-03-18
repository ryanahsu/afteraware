import requests
import airtable
from flask import Flask, request, render_template

# Set up the Airtable API client
AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appLDM3F8B89UY71p'
airtable_signups = airtable.Airtable(
    AIRTABLE_BASE_ID, 'Signups', AIRTABLE_API_KEY)
airtable_client = airtable.Airtable(AIRTABLE_BASE_ID, 'Signups', AIRTABLE_API_KEY)

url = "https://remindersdeployeduspst.uk.r.appspot.com/checkin"

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-request', methods=['POST'])
def send_request():
    patient_numbers = []
    records = airtable_client.get_all()
    for record in records:
        patient_numbers.append(record['fields']['Patient Number'])

    patient_numbers = list(set(patient_numbers))

    for patient_number in patient_numbers:
        params = {"patient_number": patient_number}
        response = requests.post(url, params=params)

    if response.status_code == 200:
        return "POST request sent successfully"
    else:
        return "Error sending POST request: {}".format(response.text)

if __name__ == '__main__':
    app.run(debug=True)