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
        color: "#66000000"
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
                            color: "#20ffffff"
                            border.width: 1
                            border.color: "#4a6b58"

                            Item {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 16

                                Text {
                                    id: symbolText
                                    text: modelData.symbol
                                    color: "#effaf2"
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
                    spacing: 14

                    Row {
                        spacing: 6
                        anchors.horizontalCenter: parent.horizontalCenter
                        SevenSegmentText {
                            value: root.dashboardModel ? root.dashboardModel.timeText : "--:--"
                            activeColor: "#ff3b3b"
                            inactiveColor: "transparent"
                            glyphWidth: 66
                            glyphHeight: 110
                            glyphSpacing: 6
                        }

                        SevenSegmentText {
                            value: ":" + (root.dashboardModel ? root.dashboardModel.secondsText : "--")
                            activeColor: "#ff3b3b"
                            inactiveColor: "transparent"
                            glyphWidth: 18
                            glyphHeight: 38
                            glyphSpacing: 4
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 11
                        }

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.periodText : "--"
                            color: "#ff3b3b"
                            font.pixelSize: 26
                            font.family: "DejaVu Sans Mono"
                            font.bold: true
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 13
                        }
                    }

                    Text {
                        text: root.dashboardModel
                              ? (root.dashboardModel.weekdayText + "  " + root.dashboardModel.dateText + "  " + root.dashboardModel.yearText)
                              : "--- --- ----"
                        color: "#d8ebf8"
                        font.pixelSize: 23
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
                            color: "#dff1ff"
                            font.pixelSize: 20
                            font.bold: true
                        }
                    }

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 5

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.currentSalahText : "--"
                            color: "#8ee7ff"
                            font.pixelSize: 30
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.nextSalahText : "--"
                            color: "#ffd995"
                            font.pixelSize: 31
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.timeLeftText : "--H --M LEFT"
                            color: "#aaff7a"
                            font.pixelSize: 22
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
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
                            color: "#20ffffff"
                            border.width: 1
                            border.color: "#6c6a45"

                            Item {
                                anchors.fill: parent
                                anchors.leftMargin: 16
                                anchors.rightMargin: 14

                                Text {
                                    id: stockSymbolText
                                    text: modelData.symbol
                                    color: "#fff4dc"
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
                    color: "#20ffffff"
                    border.width: 1
                    border.color: "#48604c"

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.verticalCenter: parent.verticalCenter
                        spacing: 1

                        Text {
                            text: modelData.day
                            color: "#e6f2ff"
                            font.pixelSize: 20
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
                            color: "#b8704f"
                            font.pixelSize: 16
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Text {
                            text: modelData.low
                            color: "#4d8fae"
                            font.pixelSize: 16
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
}
