from flask import Flask
import datetime
app = Flask(__name__)



@app.route('/')
def local_time():
    now = datetime.datetime.now()
    current_time = now.strftime('%H:%M:%S')
    return f'<h1>Current Time Is {current_time}</h1>'


def main():
    app.run(host='0.0.0.0', port=8080)