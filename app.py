from flask import Flask, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return 'shou dao q2'


@socketio.on('connect')
def test_connect():
    print('Client connected')


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')


@socketio.on('message')
def handle_message(message):
    print('Received message: ' + message)

    counter = 0
    while counter < 5:
        socketio.emit('response')
        counter += 1

    # socketio.emit('response', message)
    # socketio.emit('response')


if __name__ == '__main__':
    app.run()
