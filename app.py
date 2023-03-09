from flask import Flask, request
from flask_socketio import SocketIO, emit
import pytchat
import json
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

pre = "@" * 30

VIDEO_ID = "jfKfPfyJRdk"

chatSpeed = 3

user2socket = {}

socket2user = {}


@app.route("/")
def index():
    return "2023.03.02 K"


@socketio.on("connect")
def handle_connect(sid):
    print(f"{pre} Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"{pre} Client disconnected")


@socketio.on("createChatObject")
def handle_createChatObject():
    print(f"{pre} createChatObject")
    global chatObj

    try:
        chatObj = pytchat.create(video_id=VIDEO_ID, interruptable=False)
        chatObj.raise_for_status()

        return True
    except Exception as e:
        print(f"{pre} Failed to create chat object: {str(e)}")
        return False


@socketio.on("startProcess")
def handle_startProcess():
    print(f"{pre} startProcess 1")

    try:
        if chatObj.is_alive():
            while chatObj.is_alive():
                print(f"{pre} startProcess 2")
                chatdata = chatObj.get()
                chatObj.raise_for_status()
                socketio.emit("chatsData", chatdata.json())
                time.sleep(chatSpeed)
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to retrieve chat messages: {str(e)}")
        return False


@socketio.on("terminateProcess")
def handle_terminateProcess():
    print(f"{pre} terminateProcess")

    try:
        chatObj.terminate()
        chatObj.raise_for_status()

        return True
    except Exception as e:
        print(f"{pre} Failed to terminate chat object: {str(e)}")
        return False


@socketio.on("updateChatSpeed")
def handle_chatSpeed(seconds):
    global chatSpeed
    chatSpeed = seconds
    return True


@socketio.on("updateVid")
def handle_updateVid(id):
    global VIDEO_ID
    VIDEO_ID = id
    return True


@socketio.on("inspectChatObject")
def inspect_chat_obj():
    print(pre + " inspectChatObject")

    result = {
        "req_name": "inspectChatObject",
        "chatObj_exists": False,
        "chatObj_id": None,
        "flag_is_alive": False,
    }

    global chatObj

    if "chatObj" not in locals() and "chatObj" not in globals():
        print(pre + "chatObj variable is not defined")
        return result

    elif chatObj:
        result["chatObj_exists"] = True
        result["chatObj_id"] = id(chatObj)
        result["flag_is_alive"] = chatObj.is_alive()

    else:
        print(pre + "chatObj doesn't exist")

    return result


if __name__ == "__main__":
    socketio.run(app)
