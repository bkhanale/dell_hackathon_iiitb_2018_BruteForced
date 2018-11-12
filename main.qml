import QtQuick 2.7
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3

ApplicationWindow {
    id: win
    visible: true
    width: 1000
    height: 800
    title: "hey"

    signal loadChatRoom()

    onLoadChatRoom: {
        width = 2000
        height = 1500
        loader.source = "ChatRoom.qml"
        //irc.getNick()
    }

    Loader {
        id: loader
        source: "Options.qml"
        anchors.centerIn: parent
        active: true
        anchors.fill: parent
        onStatusChanged: {
            if(status == Loader.Ready)
                console.log("loaded")
        }
    }

    Connections {
        target: irc
        onSendNick: loader.item.nickName = nick
        onRenderNewMessage: {
            loader.item.messages.append({"msg": message[0]['text'], "user_name": message[0]['user_name'], "time": message[0]['time']})
        }
    }
}
