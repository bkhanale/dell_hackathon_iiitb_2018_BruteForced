import QtQuick 2.6
import QtQuick.Controls 1.5
import QtQuick.Controls.Styles 1.4

Rectangle {
	id: options
	readonly property var producers: ["Producer1", "Producer2", "Producer3"]
    color: "#007CBA"

	Column {
		spacing: 4
        width: parent.width / 2
        height: parent.height / 2
        anchors.centerIn: parent
		Repeater {
        id: rep
		anchors.fill: parent
		model: 3
		Button {
			id: pro
            width: rep.width
            height: rep.height / 3.2
            anchors.horizontalCenter: rep.horizontalCenter
            text: options.producers[index]
            onClicked: {
                irc.getID(text)
                win.loadChatRoom()
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
                property string currentTheme: "light"
                border.width: 2
                border.color: pro.themes[currentTheme].borderColor
                radius: 10
                gradient: Gradient {
                    GradientStop { position: 0 ; color: pro.pressed ? pro.themes[currentTheme].selectedColorGradient0 : pro.themes[currentTheme].backgroundColorGradient0 }
                    GradientStop { position: 1 ; color: pro.pressed ? pro.themes[currentTheme].selectedColorGradient1 : pro.themes[currentTheme].backgroundColorGradient1 }
                    }
                }

                label: Item {
                    id: labelItem
                    anchors.fill: parent
                    implicitWidth: labelText.implicitWidth
                    implicitHeight: labelText.implicitHeight
        
                    property string currentTheme: "light"

                    Text {
                        id: labelText
                        color: pro.themes[currentTheme].textColor
                        text: pro.text
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
        }
	}
}