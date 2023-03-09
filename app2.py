from flask import Flask
from flask_socketio import SocketIO, emit
import pytchat

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

# Define the video ID to get the chat for
VIDEO_ID = "jfKfPfyJRdk"

pre = "@" * 80

chatSpeed = 5

user2socket = {}

socket2user = {}

# create the chatObj
chatObj = pytchat.create(video_id=VIDEO_ID, interruptable=False)

@app.route("/")
def index():
    return "2023.03.02 f"


@socketio.on("connect")
def handle_connect(sid):
    print(f"{pre} Client connected")


@socketio.on("disconnect")
def handle_disconnect():
    print(f"{pre} Client disconnected")

# exam the status of the chatObj
@socketio.on("examChatObject")
def exam_chatObj():
    print(pre + " exam_chatObj")

    result1 = {
        "req_name": "exam_chatObj",
        "chatObj_exists": False,
        "chatObj_id": None,
        "flag_is_alive": None,
    }

    try:
        if "chatObj" in globals():
            result1["chatObj_exists"] = True
            result1["chatObj_id"] = id(chatObj)
            result1["flag_is_alive"] = chatObj.is_alive()
        else:
            print(pre + "chatObj doesnt exist")
            
        return result1

# create the chatObj
@socketio.on("createChatObject")
def handle_createChatObject():
    global chatObj
    chatObj = pytchat.create(video_id=VIDEO_ID, interruptable=False)


# destroy the chatObj
@socketio.on("deleteChatObject")
def handle_deleteChatObject():
    global chatObj
    del chatObj

#start fetching youtube live chat data
@socketio.on("startProcess")
def handle_startProcess():
    while chatObj.is_alive():
        for c in chatObj.get().sync_items():
            socketio.emit("chat_message", {"message": c.message, "author": c.author.name}, broadcast=True)


# try to get error info from chatObj
# raise_for_status():
# Raise internal exception after is_alive() becomes False.
# By this function, you can check the reason for the termination.
# *This function is valid only when hold_exception option is True.
@socketio.on("getExceptionInfo")
def handle_getExceptionInfo():
    try:
        chatObj._is_alive = False
        e = chatObj.raise_for_status()

    return e


# stop chatObj from fetching youtube live chat data
# terminate 等价于 self._is_alive = False 加上 self.processor.finalize()
@socketio.on("terminateProcess")
def handle_terminateProcess():
    chatObj.terminate()


# change the chatObj is_alive attribute
@socketio.on("pauseAlive")
def handle_pauseAlive(bool):
    chatObj._is_alive = bool

# change the speed of the chatObj
@socketio.on("updateChatSpeed")
def handle_chatSpeed(seconds):
    global chatSpeed
    chatSpeed = seconds

# change the video id of the chatObj
@socketio.on("updateVid")
def handle_updateVid(id):
    global VIDEO_ID
    global chatObj
    VIDEO_ID = id
    chatObj = pytchat.create(video_id=VIDEO_ID, interruptable=False)


if __name__ == "__main__":
    socketio.run(app)
