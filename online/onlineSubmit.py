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
    clinic = request.form.get("input-clinics")
    reminder = request.form.get("input-reminder")
    times = request.form.getlist("input-time[]")
    phone = "+1" + phone

    print(f"You entered text: {text}, phone: {phone}, clinic: {clinic}, reminder: {reminder}, and times: {times}")

    # Remove duplicate times
    times = list(set(times))

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

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')