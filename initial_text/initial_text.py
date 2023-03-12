# app2.py
from flask import Flask

app = Flask(__name__)

@app.route('/post')
def hello_world():
    return 'Hello, World from app2!'

if __name__ == '__main__':
    app.run(port=8000)
