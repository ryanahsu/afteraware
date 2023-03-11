import airtable
from flask import Flask, render_template, request

app = Flask(__name__)

AIRTABLE_API_KEY = 'keyiBU3kbqq2MMpOC'
AIRTABLE_BASE_ID = 'appFzlyJRq6XYKsIH'
AIRTABLE_TABLE_NAME = 'table 1'
airtable_client = airtable.Airtable(AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, AIRTABLE_API_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    text = request.form.get("input-text")
    phone = request.form.get("input-phone")
    reminder = request.form.get("input-reminder")
    times = request.form.getlist("input-time[]")
    phone = "+1" + phone

    print(f"You entered text: {text}, phone: {phone}, reminder: {reminder}, and times: {times}")

    # Remove duplicate times
    times = list(set(times))

    for time in times:
        record = {'Name': time, 'Values': phone}
        airtable_client.insert(record)

    return "Data received successfully!"


if __name__ == "__main__":
    app.run(debug=True, host='signup.afteraware.com')
