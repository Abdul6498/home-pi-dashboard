import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import "."

Window {
    id: root
    width: 1024
    height: 600
    visible: false
    color: "#020202"
    title: "Home Pi Dashboard"
    property var dashboardModel: (typeof dashboard !== "undefined" && dashboard) ? dashboard : null
    property bool missedPrayerPopupVisible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false

    Rectangle {
        anchors.fill: parent
        color: "#020202"
    }

    Image {
        id: seasonalBackground
        anchors.fill: parent
        source: root.dashboardModel ? root.dashboardModel.backgroundImageUrl : ""
        fillMode: Image.PreserveAspectCrop
        smooth: true
        visible: source !== ""
        z: 0
    }

    Rectangle {
        anchors.fill: parent
        color: "#4a000000"
        z: 0
    }

    Item {
        id: meadow
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        height: 160
        z: 0
        visible: !seasonalBackground.visible

        Rectangle {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 70
            color: "#08140b"
            opacity: 0.88
        }

        Repeater {
            model: 42
            delegate: Rectangle {
                width: 10 + (index % 5) * 4
                height: 52 + (index % 6) * 14
                radius: width / 2
                color: index % 3 === 0 ? "#153a22" : (index % 3 === 1 ? "#1c4b2a" : "#245632")
                anchors.bottom: parent.bottom
                x: (index * 25) % root.width
                rotation: index % 2 === 0 ? -18 + (index % 4) * 4 : 14 - (index % 4) * 4
                opacity: 0.72
            }
        }

        Repeater {
            model: 26
            delegate: Rectangle {
                width: 8 + (index % 4) * 3
                height: 36 + (index % 5) * 10
                radius: width / 2
                color: index % 2 === 0 ? "#2f6239" : "#3f7348"
                anchors.bottom: parent.bottom
                x: 8 + (index * 39) % root.width
                rotation: index % 2 === 0 ? 26 : -24
                opacity: 0.58
            }
        }

        Repeater {
            model: 8
            delegate: Item {
                width: 26
                height: 70
                anchors.bottom: parent.bottom
                x: 34 + index * 118

                Rectangle {
                    width: 4
                    height: 38
                    radius: 2
                    color: "#24492b"
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    opacity: 0.7
                }

                Rectangle {
                    id: flowerHead
                    width: 14
                    height: 14
                    radius: 7
                    color: index % 3 === 0 ? "#e0c36d" : (index % 3 === 1 ? "#cf8aa2" : "#d9ddd8")
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.bottom: parent.bottom
                    anchors.bottomMargin: 34
                    opacity: 0.55
                }

                Rectangle {
                    width: 8
                    height: 8
                    radius: 4
                    color: "#cfc689"
                    anchors.centerIn: flowerHead
                    opacity: 0.55
                }
            }
        }
    }

    Item {
        anchors.fill: parent
        anchors.margins: 18
        z: 1

        RowLayout {
            id: topRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: forecastRow.top
            anchors.bottomMargin: 14
            spacing: 18

            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 0.88
                Layout.fillHeight: true

                Column {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    spacing: 10

                    Repeater {
                        model: root.dashboardModel ? root.dashboardModel.cryptoItems : []
                        delegate: Rectangle {
                            width: 230
                            height: 78
                            radius: 24
                            color: "#2fffffff"
                            border.width: 1
                            border.color: "#8ed2a8"

                            Item {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 16

                                Text {
                                    id: symbolText
                                    text: modelData.symbol
                                    color: "#ffffff"
                                    font.pixelSize: 18
                                    font.bold: true
                                    anchors.left: parent.left
                                    anchors.top: parent.top
                                    anchors.topMargin: 13
                                }
                                Text {
                                    text: modelData.price
                                    color: modelData.priceColor
                                    font.pixelSize: 15
                                    font.bold: true
                                    anchors.left: symbolText.right
                                    anchors.leftMargin: 6
                                    anchors.right: parent.right
                                    anchors.top: parent.top
                                    anchors.topMargin: 13
                                    elide: Text.ElideRight
                                }
                                Text {
                                    id: changeText
                                    text: modelData.change
                                    color: modelData.changeColor
                                    font.pixelSize: 15
                                    font.bold: true
                                    anchors.left: parent.left
                                    anchors.top: symbolText.bottom
                                    anchors.topMargin: 8
                                }
                            }
                        }
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 1.7
                Layout.fillHeight: true

                Column {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 4
                    spacing: 10

                    Row {
                        spacing: 6
                        anchors.horizontalCenter: parent.horizontalCenter
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.timeText : "--:--"
                            color: "#8dff2f"
                            font.pixelSize: 96
                            font.family: "DejaVu Sans"
                            font.bold: true
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.secondsText : "--"
                            color: "#8dff2f"
                            font.pixelSize: 34
                            font.family: "DejaVu Sans"
                            font.bold: true
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 18
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.periodText : "--"
                            color: "#8dff2f"
                            font.pixelSize: 28
                            font.family: "DejaVu Sans"
                            font.bold: true
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 20
                        }
                    }

                    Text {
                        text: root.dashboardModel
                              ? (root.dashboardModel.weekdayText + "  " + root.dashboardModel.dateText + "  " + root.dashboardModel.yearText)
                              : "--- --- ----"
                        color: "#f0f7ff"
                        font.pixelSize: 22
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Row {
                        spacing: 10
                        anchors.horizontalCenter: parent.horizontalCenter

                        WeatherIcon {
                            width: 34
                            height: 28
                            kind: root.dashboardModel ? root.dashboardModel.weatherConditionKind : "cloudy"
                            primaryColor: root.dashboardModel ? root.dashboardModel.weatherIconColor : "#68c8ff"
                            secondaryColor: "#dff1ff"
                        }
                        Text {
                            text: root.dashboardModel
                                  ? (root.dashboardModel.weatherSummary.toUpperCase() + "  " + root.dashboardModel.temperatureText + "  " + root.dashboardModel.humidityText)
                                  : "--"
                            color: "#ffffff"
                            font.pixelSize: 20
                            font.bold: true
                        }
                    }

                    Item {
                        id: prayerAlertBox
                        anchors.horizontalCenter: parent.horizontalCenter
                        width: prayerBlock.implicitWidth
                        height: prayerBlock.implicitHeight

                        Column {
                            id: prayerBlock
                            anchors.centerIn: parent
                            spacing: 4

                            Text {
                                text: root.dashboardModel ? root.dashboardModel.currentSalahText : "--"
                                color: "#6ee6ff"
                                font.pixelSize: 30
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            Text {
                                text: root.dashboardModel ? root.dashboardModel.nextSalahText : "--"
                                color: "#ffe28f"
                                font.pixelSize: 31
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                            Text {
                                text: root.dashboardModel ? root.dashboardModel.timeLeftText : "--H --M LEFT"
                                color: "#b8ff69"
                                font.pixelSize: 22
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }

                        SequentialAnimation on opacity {
                            id: prayerBlink
                            running: root.dashboardModel ? root.dashboardModel.prayerAlertActive : false
                            loops: Animation.Infinite
                            NumberAnimation { to: 0.2; duration: 420 }
                            NumberAnimation { to: 1.0; duration: 420 }
                            onRunningChanged: {
                                if (!running) {
                                    prayerAlertBox.opacity = 1.0
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.dashboardModel) {
                                    root.dashboardModel.acknowledgePrayerAlert()
                                }
                                prayerAlertBox.opacity = 1.0
                            }
                        }
                    }

                    Rectangle {
                        width: 92
                        height: 38
                        radius: 19
                        color: "#24000000"
                        border.width: 1
                        border.color: "#ffd34d"
                        visible: root.dashboardModel ? root.dashboardModel.missedPrayerNotificationVisible : false
                        anchors.horizontalCenter: parent.horizontalCenter

                        Row {
                            anchors.centerIn: parent
                            spacing: 8

                            Canvas {
                                id: bellIcon
                                width: 22
                                height: 22
                                onPaint: {
                                    const ctx = getContext("2d")
                                    ctx.reset()

                                    // Bell body
                                    ctx.fillStyle = "#f5bd1f"
                                    ctx.beginPath()
                                    ctx.moveTo(4, 14)
                                    ctx.lineTo(18, 14)
                                    ctx.quadraticCurveTo(20, 14, 20, 16)
                                    ctx.quadraticCurveTo(20, 18, 18, 18)
                                    ctx.lineTo(4, 18)
                                    ctx.quadraticCurveTo(2, 18, 2, 16)
                                    ctx.quadraticCurveTo(2, 14, 4, 14)
                                    ctx.closePath()
                                    ctx.fill()

                                    // Dome
                                    ctx.beginPath()
                                    ctx.arc(11, 11, 7, Math.PI, 0, false)
                                    ctx.fill()

                                    // Bell top
                                    ctx.fillRect(10, 3, 2, 2)

                                    // Clapper
                                    ctx.fillStyle = "#f08a00"
                                    ctx.beginPath()
                                    ctx.arc(11, 18, 2, 0, Math.PI * 2, false)
                                    ctx.fill()
                                }
                            }

                            Rectangle {
                                width: 24
                                height: 24
                                radius: 12
                                color: "#ff4a4a"

                                Text {
                                    anchors.centerIn: parent
                                    text: root.dashboardModel ? root.dashboardModel.missedPrayerCount : 0
                                    color: "white"
                                    font.pixelSize: 14
                                    font.bold: true
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.dashboardModel) {
                                    root.dashboardModel.showMissedPrayerOverlay()
                                }
                            }
                        }
                    }

                    Rectangle {
                        id: missedPrayerPopup
                        width: 220
                        height: missedPrayerContent.implicitHeight + 28
                        z: 4
                        visible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false
                        anchors.horizontalCenter: parent.horizontalCenter
                        radius: 18
                        color: "#c8141414"
                        border.width: 1
                        border.color: "#ffd34d"

                        Column {
                            id: missedPrayerContent
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 8

                            Text {
                                text: "MISSED PRAYERS"
                                color: "#fff1bf"
                                font.pixelSize: 18
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Repeater {
                                model: root.dashboardModel ? root.dashboardModel.missedPrayerItems : []
                                delegate: Text {
                                    width: 180
                                    text: modelData
                                    color: "#ffffff"
                                    font.pixelSize: 16
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                }
                            }
                        }

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.dashboardModel) {
                                    root.dashboardModel.hideMissedPrayerOverlay()
                                }
                            }
                        }
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 0.88
                Layout.fillHeight: true

                Column {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    spacing: 10

                    Repeater {
                        model: root.dashboardModel ? root.dashboardModel.stockItems : []
                        delegate: Rectangle {
                            width: 230
                            height: 72
                            radius: 24
                            color: "#2fffffff"
                            border.width: 1
                            border.color: "#e7d7a0"

                            Item {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 14

                                Text {
                                    id: stockSymbolText
                                    text: modelData.symbol
                                    color: "#fffbe9"
                                    font.pixelSize: 15
                                    font.bold: true
                                    anchors.left: parent.left
                                    anchors.top: parent.top
                                    anchors.topMargin: 13
                                }
                                Text {
                                    id: stockPriceText
                                    text: modelData.price
                                    color: modelData.priceColor
                                    font.pixelSize: 14
                                    font.bold: true
                                    anchors.left: stockSymbolText.right
                                    anchors.leftMargin: 5
                                    anchors.right: parent.right
                                    anchors.top: parent.top
                                    anchors.topMargin: 13
                                    elide: Text.ElideRight
                                }
                                Text {
                                    id: stockChangeText
                                    text: modelData.change
                                    color: modelData.changeColor
                                    font.pixelSize: 14
                                    font.bold: true
                                    anchors.left: parent.left
                                    anchors.top: stockSymbolText.bottom
                                    anchors.topMargin: 7
                                }
                            }
                        }
                    }
                }
            }
        }

        RowLayout {
            id: forecastRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            height: 126
            spacing: 8

            Repeater {
                model: root.dashboardModel ? root.dashboardModel.forecastItems : []
                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 24
                    color: "#2fffffff"
                    border.width: 1
                    border.color: "#9bc7b0"

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1

                        Text {
                            text: modelData.day
                            color: "#ffffff"
                            font.pixelSize: 30
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        WeatherIcon {
                            width: 34
                            height: 26
                            kind: modelData.iconKind || "cloudy"
                            primaryColor: modelData.iconColor || "#68c8ff"
                            secondaryColor: "#dff1ff"
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: modelData.high
                            color: "#ffb35c"
                            font.pixelSize: 26
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Text {
                            text: modelData.low
                            color: "#73dcff"
                            font.pixelSize: 26
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        anchors.fill: parent
        color: "#f0000000"
        visible: root.dashboardModel ? root.dashboardModel.showPostAdhanImage : false
        z: 5

        Image {
            anchors.fill: parent
            source: root.dashboardModel ? root.dashboardModel.postAdhanImageUrl : ""
            fillMode: Image.PreserveAspectFit
            smooth: true
        }
    }

    MouseArea {
        anchors.fill: parent
        z: 2
        visible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false
        onClicked: {
            if (root.dashboardModel) {
                root.dashboardModel.hideMissedPrayerOverlay()
            }
        }
    }
}
