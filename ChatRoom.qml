import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4

Item {
    id: chatRoom

    property string nickName: ""
    property alias messages: messages
    readonly property string windowName: nickName + "'s chat window"

    Rectangle {
        anchors.fill: parent
        color: "#007CBA"
    }

    ListModel {
        id: messages
    }

    GridView {
        id: chatArea
        width: parent.width
        height: messageField.y - 50
        anchors.top: parent.top
        anchors.topMargin: 20
        cellWidth: width
        cellHeight: height / 17.6
        model: messages
        clip: true
        delegate: Item {
            width: chatArea.width
            height: chatArea.cellHeight
            Rectangle {
                id: messagePlate
                radius: height / 4
                width: messageInstance.contentWidth + 20
                height: parent.height - 5
                color: user_name === chatRoom.nickName ? "#b3ffb3" : "#ffffb3"
                anchors.horizontalCenter: messageInstance.horizontalCenter
            }

            Text {
                id: messageInstance
                font.pixelSize: 20
                height: parent.height - 8
                anchors.left: user_name === chatRoom.nickName ? undefined : parent.left
                anchors.right: user_name === chatRoom.nickName ? parent.right : undefined
                anchors.margins: 12
                text: user_name === chatRoom.nickName ? msg : "<i><b>" + user_name + ":     </b></i>" + msg
                anchors.top: parent.top
                anchors.topMargin: 7
            }
        }
    }

    TextField {
        id: messageField
        width: parent.width - 100
        height: parent.height / 16
        font.pixelSize: 25
        placeholderText: "Type your message"
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        anchors.margins: 20
        verticalAlignment: TextInput.AlignVCenter
        selectByMouse: true
        focus: true
        style: TextFieldStyle {
            textColor: "black"
            background: Rectangle {
                border.color: "black"
                border.width: 1
                radius: messageField.height / 2
            }
        }
        onAccepted: okButton.sendMessage()
    }

    Image {
        id: okButton
        width: parent.width - messageField.x - messageField.width
        anchors.left: messageField.right
        height: messageField.height / 1.2
        sourceSize.width: width
        sourceSize.height: height
        fillMode: Image.PreserveAspectFit
        anchors.verticalCenter: messageField.verticalCenter
        source: "Send.svg"

        signal sendMessage
        onSendMessage: {
            if(messageField.text)   
                irc.send_extracted_message(messageField.text)
            messageField.text = ""
        }

        MouseArea {
            anchors.fill: parent
            onPressed: {
                parent.scale = 0.85
            }
            onReleased: {
                parent.scale = 1
                parent.sendMessage()
            }
        }
    }

    Component.onCompleted: messageField.forceActiveFocus()
}
