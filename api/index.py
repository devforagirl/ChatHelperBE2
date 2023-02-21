import json
import pytchat
import time
from flask import Flask, request
from flask_socketio import SocketIO
# from flask_cors import CORS


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"

# CORS(app)

# socketio = SocketIO(app, cors_allowed_origins='*')
socketio = SocketIO(app)

pre = "@" * 80

currentVid = "86YLFOog4GM"

chatSpeed = 5

user2socket = {}

socket2user = {}


@app.route("/")
def home():
    return "Hello, World! add SocketIO cors-vercel.json"
    # return str(chatSpeed)


@socketio.on("examChatObject")
def exam_chatObj():
    print(pre + " exam_chatObj")

    result1 = {
        "req_name": "exam_chatObj",
        "chatObj_exists": False,
        # "chatObj_nonempty": False,
        "chatObj_id": None,
        "flag_is_alive": None,
    }

    try:
        # chatObj是否存在?
        if "chatObj" in globals():
            result1["chatObj_exists"] = True
            result1["chatObj_id"] = id(chatObj)
            result1["flag_is_alive"] = chatObj.is_alive()
            # result1["chatObj_nonempty"] = True
        else:
            print(pre + "chatObj doesnt exist")

        return result1
    except Exception as e:
        print(pre + "e", type(e), str(e))
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})


@socketio.on("createChatObject")
def handle_createChatObject():
    global chatObj

    try:
        chatObj = pytchat.create(video_id=currentVid)
    except Exception as e:
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})
        return

    fb = {"res_code": 1, "req_name": "createChatObject", "chatObj_id": id(chatObj)}

    return fb


# DONE
@socketio.on("deleteChatObject")
def handle_deleteChatObject():
    print(pre + "handle_deleteChatObject BEGIN")
    global chatObj

    try:
        del chatObj
    except Exception as e:
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})
        return

    print(pre + "handle_deleteChatObject END")

    fb = {
        "res_code": 1,
        "req_name": "deleteChatObject",
        "chatObj_exists": "chatObj" in globals(),
    }

    return fb


@socketio.on("initProcess")
def handle_initProcess(params):
    # 改速度
    global chatSpeed
    chatSpeed = params["chatsSpeed"]

    # 改video id
    global currentVid
    currentVid = params["currentVid"]

    # 发送状态给预设值给前端
    fb = {
        "res_code": 1,
        "req_name": "initProcess",
        "currentVid": currentVid,
        "chatsSpeed": chatSpeed,
        "vid_is_replay": chatObj.is_replay(),
        "chatObj_id": id(chatObj),
    }

    chatObj.__init__(currentVid)

    return fb


@socketio.on("startProcess")
def handle_startProcess():
    while True:
        if "chatObj" not in globals() or not chatObj.is_alive():
            print(pre + "while break")
            break

        chatdata = chatObj.get()
        socketio.emit("chatsData", chatdata.json())
        time.sleep(chatSpeed)

    try:
        chatObj.raise_for_status()
    except Exception as e:
        print(type(e), str(e))
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})
        return "Error occurred. Already sent it through exceptionInfo emit"

    return "startProcess finished"


# raise_for_status():
# Raise internal exception after is_alive() becomes False.
# By this function, you can check the reason for the termination.
# *This function is valid only when hold_exception option is True.
@socketio.on("getExceptionInfo")
def handle_getExceptionInfo():
    fb = {}
    try:
        chatObj._is_alive = False
        e = chatObj.raise_for_status()
        fb = {
            "res_code": 1,
            "req_name": "getExceptionInfo",
            "type": str(type(e)),
            "content": str(e),
        }
    except Exception as e:
        fb = {
            "res_code": 0,
            "req_name": "getExceptionInfo",
            "type": str(type(e)),
            "content": str(e),
        }

    return fb


# terminate 等价于 self._is_alive = False 加上 self.processor.finalize()
@socketio.on("terminateProcess")
def handle_terminateProcess():
    print(pre + "handle_terminateProcess BEGIN")
    try:
        chatObj.terminate()

        fb = {
            "res_code": 1,
            "req_name": "terminateProcess",
            "chatObj_id": id(chatObj),
            "flag_is_alive": chatObj.is_alive(),
        }

        return fb
    except Exception as e:
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})
    print(pre + "handle_terminateProcess END")


# 前端的pause按钮
@socketio.on("pauseAlive")
def handle_pauseAlive(bool):
    try:
        chatObj._is_alive = bool

        fb = {
            "res_code": 1,
            "req_name": "pauseAlive",
            "chatObj_id": id(chatObj),
            "flag_is_alive": chatObj.is_alive(),
        }

        return fb

    except Exception as e:
        socketio.emit("exceptionInfo", {"type": str(type(e)), "content": str(e)})


@socketio.on("updateChatSpeed")
def handle_chatSpeed(seconds):
    print("handle_chatSpeed->", seconds)

    global chatSpeed
    chatSpeed = seconds

    fb = {"res_code": 1, "req_name": "updateChatSpeed", "chatSpeed": chatSpeed}

    return fb


@socketio.on("updateVid")
def handle_updateVid(id):
    global currentVid
    currentVid = id

    fb = {
        "res_code": 1,
        "req_name": "updateVid",
        "currentVid": currentVid,
        "note": "RESTART NEEDED",
    }

    return fb


@socketio.on("check_user_exist")
def handle_message(message):
    print("received message: " + message)
    return True


# DONE
# 用户进入
@socketio.on("userEnter")
def handle_userEnter(nickname):
    sid = request.sid

    user2socket[nickname] = sid
    socket2user[sid] = nickname

    print(pre + "userEnter", user2socket, socket2user)

    socketio.emit("bcUserEntered", nickname, broadcast=True)

    return {"room_info": {"user2socket": user2socket}}


# DONE
# 用户退出
@socketio.on("userLeave")
def handle_userLeave():
    # 在两表中删除该用户
    sid = request.sid
    nickname = socket2user[sid]

    del user2socket[nickname]
    del socket2user[sid]

    print(pre + "userLeave", nickname)

    socketio.emit("bcUserLeft", nickname, broadcast=True)

    return {"name": nickname}


# DONE
@socketio.on("connect")
def handle_userDisconnect():
    print(pre + " connect")


@socketio.on("disconnect")
def handle_userDisconnect():
    print(pre + " disconnect")
    # 防止用户在登陆页面刷新造成的报错
    if user2socket == {} or socket2user == {}:
        return print(pre + "one of the two lists is empty，return.")

    # 在两表中删除该用户
    sid = request.sid
    nickname = socket2user[sid]

    del user2socket[nickname]
    del socket2user[sid]

    # 结束chatObj实例
    handle_terminateProcess()

    # TODO 返回到前端| @@@@ 都disconnected了，应该收不到返回值了吧
    fb = {"res_code": 1, "req_name": "disconnect"}
    socketio.emit("cmdFeedback", fb)

    # 广播用户离开事件
    socketio.emit("user_leave", nickname, broadcast=True)


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
