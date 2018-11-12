import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4

Item {
    id: formWindow

    readonly property var placeholderTexts: ["127.0.0.1", "Your Name"]
    readonly property var labels: ["Host:", "Nick:"]
    readonly property var regExps: [/((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}/, /^[A-Z|a-z]+[_|0-9]*/]
    readonly property string windowName: "Login"

    Rectangle {
        anchors.fill: parent
        color: "#007CBA"
    }

    Image {
        id: dellLogo
        source: "logo2.jpg"
        width: parent.width / 1.7
        height: parent.height / 2
        fillMode: Image.PreserveAspectFit
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
    }

    Item {
        width: parent.width
        height: parent.height - dellLogo.paintedHeight
        anchors.top: dellLogo.bottom
        Column {
            id: fieldColumns
            width: parent.width / 1.2
            height: parent.height / 1.8
            anchors.centerIn: parent
            spacing: 5
            Repeater {
                id: fieldRepeater
                anchors.fill: parent
                model: 2
                Row {
                    width: parent.width
                    height: parent.height / 4
                    anchors.left: parent.left
                    anchors.leftMargin: 20
                    spacing: 5
                    Item {
                        id: label
                        width: parent.width / 7
                        height: parent.height
                        anchors.verticalCenter: parent.verticalCenter
                        Text {
                            anchors.fill: parent
                            verticalAlignment: Text.AlignVCenter
                            font.pixelSize: 25
                            text: labels[index]
                            color: "white"
                        }
                    }
    
                    readonly property alias text: inputField.text

                    TextField {
                        id: inputField
                        width: parent.width / 1.4
                        height: parent.height / 1.2
                        font.pixelSize: 25
                        placeholderText: formWindow.placeholderTexts[index]
                        anchors.verticalCenter: parent.verticalCenter
                        verticalAlignment: TextInput.AlignVCenter
                        selectByMouse: true
                        style: TextFieldStyle {
                                textColor: "black"
                                background: Rectangle {
                                border.color: "black"
                                border.width: 0.5
                                radius: inputField.height / 2
                            }
                        }
                        validator: RegExpValidator { regExp: formWindow.regExps[index] }
                    }
                }
            }
        }

        Button {
            id: okButton
            width: parent.width / 4.8
            height: parent.height / 11
            text: "Ok"
            anchors {
                top: fieldColumns.bottom
                right: fieldColumns.right
                rightMargin: 20
            }

            readonly property var themes: {
                "dark": {
                    backgroundColorGradient0: "#23373737",
                    selectedColorGradient0: "#C03ACAFF",
                    backgroundColorGradient1: "#13373737",
                    selectedColorGradient1: "#803ACAFF",
                    borderColor: "#FF373737",
                    textColor: "#FF373737"
                },
                "light": {
                    backgroundColorGradient0: "#42FFFFFF",
                    selectedColorGradient0: "#C03ACAFF",
                    backgroundColorGradient1: "#23FFFFFF",
                    selectedColorGradient1: "#803ACAFF",
                    borderColor: "white",
                    textColor: "white"
                },
                "highContrast": {
                    backgroundColorGradient0: "#EEFFFFFF",
                    selectedColorGradient0: "#C03ACAFF",
                    backgroundColorGradient1: "#AAFFFFFF",
                    selectedColorGradient1: "#803ACAFF",
                    borderColor: "white",
                    textColor: "373737"
                }
            }

            style: ButtonStyle {
                background: Rectangle {
                property string currentTheme: "highContrast"
                border.width: 2
                border.color: okButton.themes[currentTheme].borderColor
                radius: 10
                gradient: Gradient {
                    GradientStop { position: 0 ; color: okButton.pressed ? okButton.themes[currentTheme].selectedColorGradient0 : okButton.themes[currentTheme].backgroundColorGradient0 }
                    GradientStop { position: 1 ; color: okButton.pressed ? okButton.themes[currentTheme].selectedColorGradient1 : okButton.themes[currentTheme].backgroundColorGradient1 }
                    }
                }

                label: Item {
                    id: labelItem
                    anchors.fill: parent
                    implicitWidth: labelText.implicitWidth
                    implicitHeight: labelText.implicitHeight
        
                    property string currentTheme: "highContrast"

                    Text {
                        id: labelText
                        color: okButton.themes[currentTheme].textColor
                        text: okButton.text
                        font.pixelSize: 22
                        anchors.fill: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        wrapMode: Text.WordWrap
                        fontSizeMode: Text.Fit
                    }
                }
            }
        }

        function isFieldValid(text) {
            if(text === "")
                return false
            return true
        }
    }
}
