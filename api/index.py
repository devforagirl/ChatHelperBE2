from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

currentVid = "86YLFOog4GM"

chatSpeed = 5


@socketio.on("updateChatSpeed")
def handle_chatSpeed(seconds):
    print("handle_chatSpeed->", seconds)

    global chatSpeed
    chatSpeed = seconds

    fb = {"res_code": 1, "req_name": "updateChatSpeed", "chatSpeed": chatSpeed}

    return fb


@socketio.on("updateVid")
def handle_updateVid(id):
    print("handle_updateVid->", id)

    global currentVid
    currentVid = id

    fb = {
        "res_code": 1,
        "req_name": "updateVid",
        "currentVid": currentVid,
        "note": "RESTART NEEDED",
    }

    return fb


@app.route("/")
def home():
    # return "Hello, World! 33345"
    return str(chatSpeed)


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
