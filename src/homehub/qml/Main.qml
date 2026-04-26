import QtQuick
import QtQuick.Window
import "."

Window {
    id: root
    width: 1024
    height: 600
    visible: false
    color: "#120f0b"
    title: "Home Pi Dashboard"

    property var dashboardModel: (typeof dashboard !== "undefined" && dashboard) ? dashboard : null
    property bool missedPrayerPopupVisible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false

    property url qiyamIcon: Qt.resolvedUrl("../assets/qiyam.png")
    property url rukuIcon: Qt.resolvedUrl("../assets/ruku.png")
    property url sajdaIcon: Qt.resolvedUrl("../assets/sajda.png")
    property url jalsaIcon: Qt.resolvedUrl("../assets/jalsa.png")
    property url itidalIcon: Qt.resolvedUrl("../assets/itidal.png")
    property url taslimIcon: Qt.resolvedUrl("../assets/taslim.png")

    property int currentPoseIndex: root.dashboardModel ? root.dashboardModel.testSalahProgressIndex : 3
    property int currentRakatIndex: root.dashboardModel ? root.dashboardModel.testRakatIndex : 1
    property var salahProgressStages: [
        { "label": "QIYAM", "icon": qiyamIcon },
        { "label": "RUKU", "icon": rukuIcon },
        { "label": "I'TIDAL", "icon": itidalIcon },
        { "label": "SAJDA", "icon": sajdaIcon },
        { "label": "JALSA", "icon": jalsaIcon },
        { "label": "SAJDA", "icon": sajdaIcon },
        { "label": "TASLIM", "icon": taslimIcon }
    ]
    property var rakatStages: [
        { "label": "Rakat 1", "value": "1" },
        { "label": "Rakat 2", "value": "2" },
        { "label": "Rakat 3", "value": "3" },
        { "label": "Rakat 4", "value": "4" },
        { "label": "Final", "value": "Ø" }
    ]
    property real timeProgressValue: root.dashboardModel ? root.dashboardModel.timeLeftProgressValue : 0.0

    Rectangle {
        anchors.fill: parent
        color: "#000000"
    }

    Item {
        id: tabletShell
        anchors.fill: parent
    }

    Item {
        id: contentArea
        anchors.fill: tabletShell
        anchors.leftMargin: 6
        anchors.rightMargin: 6
        anchors.topMargin: 6
        anchors.bottomMargin: 6

        Column {
            id: dashboardColumn
            anchors.fill: parent
            spacing: 8

            Row {
                id: headerRow
                width: parent.width
                height: 88
                spacing: 12

                Rectangle {
                    id: dateCard
                    width: 218
                    height: parent.height
                    radius: 14
                    color: "transparent"
                    border.width: 1
                    border.color: "#364048"

                    Rectangle {
                        width: 4
                        height: parent.height - 28
                        radius: 2
                        color: "#08f1d2"
                        anchors.left: parent.left
                        anchors.leftMargin: 10
                        anchors.verticalCenter: parent.verticalCenter
                    }

                    Column {
                        anchors.left: parent.left
                        anchors.leftMargin: 22
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 2

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.weekdayText + "," : "---"
                            color: "#f5f8fb"
                            font.pixelSize: 22
                            font.bold: true
                        }
                        Text {
                            text: root.dashboardModel ? (root.dashboardModel.dateText + " " + root.dashboardModel.yearText) : "---"
                            color: "#dbe4eb"
                            font.pixelSize: 15
                            font.bold: true
                        }
                    }

                    Item {
                        id: dateNotificationAnchor
                        anchors.left: parent.left
                        anchors.leftMargin: 142
                        anchors.verticalCenter: parent.verticalCenter
                        width: 54
                        height: 28
                        visible: root.dashboardModel ? root.dashboardModel.missedPrayerNotificationVisible : false

                        Canvas {
                            anchors.left: parent.left
                            anchors.verticalCenter: parent.verticalCenter
                            width: 20
                            height: 20
                            onPaint: {
                                const ctx = getContext("2d")
                                ctx.reset()
                                ctx.fillStyle = "#f5bd1f"
                                ctx.beginPath()
                                ctx.moveTo(4, 13)
                                ctx.lineTo(16, 13)
                                ctx.quadraticCurveTo(18, 13, 18, 15)
                                ctx.quadraticCurveTo(18, 17, 16, 17)
                                ctx.lineTo(4, 17)
                                ctx.quadraticCurveTo(2, 17, 2, 15)
                                ctx.quadraticCurveTo(2, 13, 4, 13)
                                ctx.closePath()
                                ctx.fill()
                                ctx.beginPath()
                                ctx.arc(10, 10, 6, Math.PI, 0, false)
                                ctx.fill()
                                ctx.fillRect(9, 2, 2, 2)
                                ctx.fillStyle = "#f08a00"
                                ctx.beginPath()
                                ctx.arc(10, 17, 2, 0, Math.PI * 2, false)
                                ctx.fill()
                            }
                        }

                        Rectangle {
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
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

                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                if (root.dashboardModel) {
                                    root.dashboardModel.showMissedPrayerOverlay()
                                }
                            }
                        }
                    }
                }

                Rectangle {
                    width: parent.width - 218 - 190 - 24
                    height: parent.height
                    radius: 14
                    color: "transparent"
                    border.width: 1
                    border.color: "#364048"

                    Row {
                        anchors.centerIn: parent
                        spacing: 8

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.timeText : "--:--"
                            color: "#f8fbff"
                            font.pixelSize: 92
                            font.bold: true
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.secondsText : "--"
                            color: "#08f1d2"
                            font.pixelSize: 32
                            font.bold: true
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 14
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.periodText : "--"
                            color: "#08f1d2"
                            font.pixelSize: 30
                            font.bold: true
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 14
                        }
                    }
                }

                Rectangle {
                    width: 190
                    height: parent.height
                    radius: 14
                    color: "transparent"
                    border.width: 1
                    border.color: "#364048"

                    Column {
                        anchors.centerIn: parent
                        spacing: 2

                        Row {
                            anchors.horizontalCenter: parent.horizontalCenter
                            spacing: 6

                            WeatherIcon {
                                width: 22
                                height: 22
                                kind: root.dashboardModel ? root.dashboardModel.weatherConditionKind : "cloudy"
                                primaryColor: root.dashboardModel ? root.dashboardModel.weatherIconColor : "#68c8ff"
                                secondaryColor: "#f4fbff"
                            }

                            Text {
                                text: root.dashboardModel ? root.dashboardModel.weatherSummary.toUpperCase() : "--"
                                color: "#f8fbff"
                                font.pixelSize: 14
                                font.bold: true
                            }
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.temperatureText : "--"
                            color: "#ffffff"
                            font.pixelSize: 24
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.humidityText + " HUMIDITY" : "--"
                            color: "#dde6ee"
                            font.pixelSize: 13
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                    }
                }
            }

            Item {
                id: prayerAlertBox
                width: parent.width
                height: 332

                Rectangle {
                    anchors.fill: parent
                    radius: 16
                    color: "transparent"
                    border.width: 1
                    border.color: "#364048"
                }

                Column {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 8

                    Item {
                        width: parent.width
                        height: 96

                        Row {
                            anchors.fill: parent
                            spacing: 12

                            Rectangle {
                                width: 230
                                height: parent.height
                                radius: 14
                                color: "transparent"
                                border.width: 1
                                border.color: "#364048"

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 1

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.hijriMonthText : ""
                                        color: "#08f1d2"
                                        font.pixelSize: 18
                                        font.bold: true
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.hijriDateText : ""
                                        color: "#f8fbff"
                                        font.pixelSize: 24
                                        font.bold: true
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.hijriYearText : ""
                                        color: "#d7e4ee"
                                        font.pixelSize: 15
                                        font.bold: true
                                    }
                                }
                            }

                            Rectangle {
                                width: parent.width - 484
                                height: parent.height
                                radius: 14
                                color: "transparent"
                                border.width: 1
                                border.color: "#364048"

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 10

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.nextSalahNameText : "PRAYER"
                                        color: "#08f1d2"
                                        font.pixelSize: 38
                                        font.bold: true
                                    }

                                    Row {
                                        spacing: 8
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        visible: root.dashboardModel
                                                 ? root.dashboardModel.currentPrayerBreakdownItems.length > 0
                                                 : false

                                        Repeater {
                                            model: root.dashboardModel ? root.dashboardModel.currentPrayerBreakdownItems : []
                                            delegate: Rectangle {
                                                width: chipTextTop.implicitWidth + 18
                                                height: 28
                                                radius: 14
                                                color: modelData.fillColor
                                                border.width: 1
                                                border.color: modelData.borderColor

                                                Text {
                                                    id: chipTextTop
                                                    anchors.centerIn: parent
                                                    text: modelData.label
                                                    color: modelData.accentColor
                                                    font.pixelSize: 13
                                                    font.bold: true
                                                }
                                            }
                                        }
                                    }
                                }
                            }

                            Rectangle {
                                width: 230
                                height: parent.height
                                radius: 14
                                color: "transparent"
                                border.width: 1
                                border.color: "#364048"

                                Column {
                                    anchors.centerIn: parent
                                    spacing: 2

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.nextSalahNameText : "NEXT PRAYER"
                                        color: "#08f1d2"
                                        font.pixelSize: 20
                                        font.bold: true
                                    }

                                    Text {
                                        anchors.horizontalCenter: parent.horizontalCenter
                                        text: root.dashboardModel ? root.dashboardModel.nextSalahTimeOnlyText : "--:--"
                                        color: "#f8fbff"
                                        font.pixelSize: 28
                                        font.bold: true
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        width: parent.width
                        height: 104
                        radius: 12
                        color: "transparent"
                        border.width: 1
                        border.color: "#343d45"

                        Item {
                            anchors.fill: parent
                            anchors.margins: 12

                            Text {
                                text: "SALAH PROGRESS"
                                color: "#ffffff"
                                font.pixelSize: 16
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.top: parent.top
                            }

                            Rectangle {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.top: parent.top
                                anchors.topMargin: 34
                                height: 4
                                radius: 2
                                color: "#374149"
                            }

                            Rectangle {
                                anchors.left: parent.left
                                anchors.top: parent.top
                                anchors.topMargin: 34
                                width: (parent.width / Math.max(1, root.salahProgressStages.length - 1)) * Math.min(root.currentPoseIndex, root.salahProgressStages.length - 1)
                                height: 4
                                radius: 2
                                color: "#08f1d2"
                            }

                            Row {
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.bottom: parent.bottom
                                spacing: 0

                                Repeater {
                                    model: root.salahProgressStages
                                    delegate: Item {
                                        width: (parent.width / root.salahProgressStages.length)
                                        height: 54

                                        property bool active: index <= root.currentPoseIndex

                                        Rectangle {
                                            width: 38
                                            height: 38
                                            radius: 19
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            anchors.top: parent.top
                                            color: active ? "#08f1d2" : "#3f464f"
                                            border.width: 1
                                            border.color: active ? "#08f1d2" : "#59626b"

                                            Image {
                                                anchors.centerIn: parent
                                                width: 22
                                                height: 22
                                                source: modelData.icon
                                                fillMode: Image.PreserveAspectFit
                                                opacity: active ? 1.0 : 0.52
                                            }
                                        }

                                        Text {
                                            anchors.horizontalCenter: parent.horizontalCenter
                                            anchors.bottom: parent.bottom
                                            text: modelData.label
                                            color: active ? "#f8fbff" : "#c5ced7"
                                            font.pixelSize: 12
                                            font.bold: true
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Row {
                        width: parent.width
                        spacing: 12

                        Rectangle {
                            id: rakatPanel
                            width: (parent.width - 12) / 2
                            height: 96
                            radius: 12
                            color: "transparent"
                            border.width: 1
                            border.color: "#343d45"

                            Column {
                                anchors.centerIn: parent
                                width: parent.width - 24
                                spacing: 10

                                Text {
                                    text: "RAKAT"
                                    color: "#dfe8f0"
                                    font.pixelSize: 18
                                    font.bold: true
                                    anchors.horizontalCenter: parent.horizontalCenter
                                }

                                Row {
                                    id: rakatRow
                                    spacing: 10
                                    anchors.horizontalCenter: parent.horizontalCenter

                                    Repeater {
                                        model: root.rakatStages
                                        delegate: Column {
                                            spacing: 4

                                            Rectangle {
                                                width: 50
                                                height: 50
                                                radius: 25
                                                color: index <= root.currentRakatIndex ? "#08f1d2" : "#353c44"
                                                border.width: 1
                                                border.color: index <= root.currentRakatIndex ? "#08f1d2" : "#59626b"
                                                anchors.horizontalCenter: parent.horizontalCenter

                                                Text {
                                                    anchors.centerIn: parent
                                                    text: modelData.value
                                                    color: index <= root.currentRakatIndex ? "#09221b" : "#ffffff"
                                                    font.pixelSize: 26
                                                    font.bold: true
                                                }
                                            }
                                        }
                                    }
                                }

                            }
                        }

                        Rectangle {
                            id: reminderPanel
                            width: (parent.width - 12) / 2
                            height: 96
                            radius: 12
                            color: "transparent"
                            border.width: 1
                            border.color: "#343d45"

                            Column {
                                anchors.centerIn: parent
                                width: parent.width - 28
                                spacing: 10

                                Row {
                                    width: parent.width

                                    Text {
                                        text: root.dashboardModel ? (root.dashboardModel.nextSalahText.split(" ")[0] + " / TIME LEFT: ") : "TIME LEFT: "
                                        color: "#ffffff"
                                        font.pixelSize: 18
                                        font.bold: true
                                    }

                                    Item { width: Math.max(0, parent.width - timeLeftValue.implicitWidth - 170) }

                                    Text {
                                        id: timeLeftValue
                                        text: root.dashboardModel ? root.dashboardModel.timeLeftText.replace(" LEFT", "") : "--:--"
                                        color: "#08f1d2"
                                        font.pixelSize: 18
                                        font.bold: true
                                    }
                                }

                                Rectangle {
                                    width: parent.width
                                    height: 18
                                    radius: 9
                                    color: "#384149"

                                    Rectangle {
                                        width: parent.width * root.timeProgressValue
                                        height: parent.height
                                        radius: 9
                                        color: "#08f1d2"
                                    }
                                }
                            }
                        }
                    }
                }

                SequentialAnimation {
                    id: reminderBlink
                    running: root.dashboardModel ? root.dashboardModel.prayerAlertActive : false
                    loops: Animation.Infinite
                    PropertyAnimation { target: reminderPanel; property: "opacity"; to: 0.35; duration: 420 }
                    PropertyAnimation { target: reminderPanel; property: "opacity"; to: 1.0; duration: 420 }
                    onRunningChanged: {
                        if (!running) {
                            reminderPanel.opacity = 1.0
                        }
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if (root.dashboardModel) {
                            root.dashboardModel.acknowledgePrayerAlert()
                        }
                        reminderPanel.opacity = 1.0
                    }
                }
            }

            Row {
                id: forecastRow
                width: parent.width
                height: dashboardColumn.height - headerRow.height - prayerAlertBox.height - (dashboardColumn.spacing * 2)
                spacing: 10

                Repeater {
                    model: root.dashboardModel ? root.dashboardModel.forecastItems.slice(0, 6) : []
                    delegate: Rectangle {
                        width: root.dashboardModel
                               ? Math.floor((forecastRow.width - ((Math.min(root.dashboardModel.forecastItems.length, 6) - 1) * forecastRow.spacing)) / Math.min(root.dashboardModel.forecastItems.length, 6))
                               : 120
                        height: parent.height
                        radius: 14
                        color: "transparent"
                        border.width: 1
                        border.color: "#384149"

                        Column {
                            anchors.centerIn: parent
                            spacing: 3

                            Text {
                                text: modelData.day
                                color: "#f7fbff"
                                font.pixelSize: 25
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            WeatherIcon {
                                width: 26
                                height: 26
                                kind: modelData.iconKind || "cloudy"
                                primaryColor: modelData.iconColor || "#68c8ff"
                                secondaryColor: "#f4fbff"
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: modelData.high
                                color: "#ffffff"
                                font.pixelSize: 23
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }

                            Text {
                                text: modelData.low
                                color: "#c9d5df"
                                font.pixelSize: 19
                                font.bold: true
                                anchors.horizontalCenter: parent.horizontalCenter
                            }
                        }
                    }
                }
            }
        }
    }

    Rectangle {
        id: missedPrayerPopup
        width: 220
        height: missedPrayerContent.implicitHeight + 28
        z: 6
        visible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false
        x: contentArea.x + dateCard.x + dateCard.width - width - 12
        y: contentArea.y + dateCard.y + dateCard.height + 10
        radius: 18
        color: "#dd141414"
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
        z: 5
        visible: root.dashboardModel ? root.dashboardModel.missedPrayerOverlayVisible : false
        onClicked: {
            if (root.dashboardModel) {
                root.dashboardModel.hideMissedPrayerOverlay()
            }
        }
    }
}
