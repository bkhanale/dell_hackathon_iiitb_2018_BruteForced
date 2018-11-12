from threading import Thread
import queue

import time
import atexit

import client_socket
import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QObject, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtQml import QQmlComponent, QQmlEngine, QQmlApplicationEngine

loginDetails = 0
chat_socket = 0
nickName = ""
receive_que = 0
socket_receive_thread = 0
render_incoming_msg_thread = 0
PORT = 33000
supplierID = "s1"
producerID = ""

def connect():
    is_connected = False
    global PORT
    while not is_connected:
        try:
            HOST = "127.0.0.1"
            if not PORT:
                PORT = 33000
            if not HOST:
                raise Exception('Host must be filled')
            address = (HOST, PORT)
            chat_socket = client_socket.create_socket(address)
            is_connected = True
        except Exception as e:
            print('error in connection to the server: ', e)
            print('lets try again, the IP must be valid, default port is 33000')
    return chat_socket


def render_incoming_msg(recieve_que):
    while True:
        try:
            msg = []
            msg.append(recieve_que.get())
            irc.renderNewMessage.emit(msg)
        except OSError as e:  # Possibly client has left the chat.
            print('err: ', e)
            print('end rendering thread')
            break


def create_json_msg(user_name, text):
    sending_time = time.strftime("%H:%M", time.localtime())
    global supplierID
    global producerID
    msg = {
        'supplierID': supplierID,
        'producerID': producerID,
        'user_name': user_name,
        'text': text,
        'time': sending_time,
    }
    return msg


def send_msg(new_msg_text):
    if nickName is not None and new_msg_text is not None:
        new_msg = create_json_msg(user_name=nickName, text=new_msg_text)
        if new_msg_text != '{quit}':
            client_socket.send_new_msg(new_msg, chat_socket)
        else:
            window.close()
            exit()


def handle_exit():
    quit_msg = create_json_msg(user_name=nickName, text='{quit}\n')
    client_socket.send_new_msg(quit_msg, chat_socket)


def startConnections():
    global loginDetails
    global chat_socket
    global nickName
    global socket_receive_thread
    global render_incoming_msg_thread
    global receive_que

    chat_socket = connect()

    receive_que = queue.Queue()

    socket_receive_thread = Thread(
        target=client_socket.receive, daemon=True, args=(
            chat_socket, receive_que,), name='socket_receive_thread')
    socket_receive_thread.start()

    render_incoming_msg_thread = Thread(
        target=render_incoming_msg,
        daemon=True,
        args=(
            receive_que,
        ))
    render_incoming_msg_thread.start()

    atexit.register(handle_exit)


class IRC(QObject):
    def __init__(self):
        QObject.__init__(self)

    sendNick = pyqtSignal(str, arguments=['nick'])
    renderNewMessage = pyqtSignal(list, arguments=['message'])

    @pyqtSlot(str)
    def getID(self, val):
        global PORT
        global producerID
        producerID = val
        print("Received: " + val)
        if val == "Producer1":
            PORT = 33000
        elif val == "Producer2":
            PORT = 33001
        else:
            PORT = 33003
        startConnections()

    @pyqtSlot(str)
    def send_extracted_message(self, msg):
        send_msg(msg)


# Initialize the software window.
app = QApplication(sys.argv)

# Create the QtQuick engine and load the software's root component.
engine = QQmlApplicationEngine()
irc = IRC()
engine.rootContext().setContextProperty("irc", irc)
component = QQmlComponent(engine)
component.loadUrl(QUrl('main.qml'))
window = component.create()

app.exec_()
