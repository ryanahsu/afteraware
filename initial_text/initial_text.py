import requests
import time
from datetime import datetime
import airtable

# Set up the Airtable API client
api_key = 'keyiBU3kbqq2MMpOC'
base_id = 'appLDM3F8B89UY71p'
table_name = 'Signups'


airtable_client = airtable.Airtable(base_id, table_name, api_key)


url = "https://1e1d-2601-602-8b81-4810-5467-8751-5261-d970.ngrok.io/checkin"


# Set the time to send the request (in 24-hour format)
send_time = "14:44"

while True:

    records = airtable_client.get_all()
    patient_numbers = []
    for record in records:
        patient_numbers.append(record['fields']['Patient Number'])

    patient_numbers = list(set(patient_numbers))  # Remove duplicates


    # Get the current time
    now = datetime.now().strftime("%H:%M")

    # If the current time matches the send time, send the request
    if now == send_time:
        for patient_number in patient_numbers:
            params = {"patient_number": patient_number}
            response = requests.post(url, params=params)

        # Check the response
        if response.status_code == 200:
            print("POST request sent successfully")
        else:
            print("Error sending POST request:", response.text)

    # Wait for 1 minute before checking the time again
    time.sleep(60)
