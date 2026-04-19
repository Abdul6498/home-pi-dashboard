import QtQuick
import QtQuick.Window
import QtQuick.Layouts

Window {
    id: root
    width: 1024
    height: 600
    visible: true
    color: "black"
    title: "Home Pi Dashboard"
    property var dashboardModel: (typeof dashboard !== "undefined" && dashboard) ? dashboard : null

    Image {
        id: bg
        anchors.fill: parent
        source: root.dashboardModel ? root.dashboardModel.backgroundImageUrl : ""
        fillMode: Image.PreserveAspectCrop
        smooth: true
    }

    Rectangle {
        anchors.fill: parent
        color: "#66000000"
    }

    Item {
        anchors.fill: parent
        anchors.margins: 18

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
                Layout.preferredWidth: 0.95
                Layout.fillHeight: true

                Column {
                    anchors.left: parent.left
                    anchors.top: parent.top
                    spacing: 14

                    Text {
                        text: "MARKETS"
                        color: "#dcecff"
                        font.pixelSize: 22
                        font.bold: true
                    }

                    Column {
                        spacing: 10

                        Text {
                            text: "CRYPTO"
                            color: "#8fd8ff"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Repeater {
                            model: root.dashboardModel ? root.dashboardModel.cryptoItems : []
                            delegate: Column {
                                spacing: 1

                                Text {
                                    text: modelData.symbol
                                    color: "#f0f6fd"
                                    font.pixelSize: 27
                                    font.bold: true
                                }
                                Text {
                                    text: modelData.price
                                    color: modelData.priceColor
                                    font.pixelSize: 20
                                    font.bold: true
                                }
                                Text {
                                    text: modelData.change
                                    color: modelData.changeColor
                                    font.pixelSize: 16
                                    font.bold: true
                                }
                            }
                        }
                    }

                    Column {
                        spacing: 8

                        Text {
                            text: "STOCKS"
                            color: "#ffb870"
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Repeater {
                            model: root.dashboardModel ? root.dashboardModel.stockItems : []
                            delegate: Column {
                                spacing: 1

                                Text {
                                    text: modelData.symbol
                                    color: "#fff0dc"
                                    font.pixelSize: 25
                                    font.bold: true
                                }
                                Text {
                                    text: modelData.price
                                    color: modelData.priceColor
                                    font.pixelSize: 19
                                    font.bold: true
                                }
                                Text {
                                    text: modelData.change
                                    color: modelData.changeColor
                                    font.pixelSize: 16
                                    font.bold: true
                                }
                            }
                        }
                    }
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.preferredWidth: 1.55
                Layout.fillHeight: true

                Column {
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.top
                    anchors.topMargin: 4
                    spacing: 10

                    Row {
                        spacing: 12
                        anchors.horizontalCenter: parent.horizontalCenter
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.timeText : "--:--"
                            color: "#f4f7fb"
                            font.pixelSize: 92
                            font.bold: true
                        }
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.periodText : "--"
                            color: "#f4f7fb"
                            font.pixelSize: 30
                            font.bold: true
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: root.dashboardModel ? root.dashboardModel.weekdayText + " " + root.dashboardModel.dateText : "--- ---"
                        color: "#d8ebf8"
                        font.pixelSize: 22
                        font.bold: true
                        anchors.horizontalCenter: parent.horizontalCenter
                    }

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        spacing: 4

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.currentSalahText : "--"
                            color: "#8ee7ff"
                            font.pixelSize: 28
                            font.bold: true
                            anchors.horizontalCenter: parent.horizontalCenter
                        }
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.nextSalahText : "--"
                            color: "#ffd995"
                            font.pixelSize: 30
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
                Layout.preferredWidth: 1.0
                Layout.fillHeight: true

                Column {
                    anchors.right: parent.right
                    anchors.top: parent.top
                    spacing: 2

                    Text {
                        text: root.dashboardModel ? root.dashboardModel.weekdayText : "---"
                        color: "#f1ea63"
                        font.pixelSize: 50
                        font.bold: true
                        horizontalAlignment: Text.AlignRight
                    }
                    Text {
                        text: root.dashboardModel ? root.dashboardModel.dateText : "--- --"
                        color: "#f1ea63"
                        font.pixelSize: 34
                        font.bold: true
                        horizontalAlignment: Text.AlignRight
                    }
                    Text {
                        text: root.dashboardModel ? root.dashboardModel.temperatureText : "--C"
                        color: "#8bf15e"
                        font.pixelSize: 52
                        font.bold: true
                        horizontalAlignment: Text.AlignRight
                    }
                    Text {
                        text: root.dashboardModel ? root.dashboardModel.humidityText : "--%"
                        color: "#8bf15e"
                        font.pixelSize: 38
                        font.bold: true
                        horizontalAlignment: Text.AlignRight
                    }
                    Row {
                        spacing: 8

                        Text {
                            text: root.dashboardModel ? root.dashboardModel.weatherIcon : ""
                            color: root.dashboardModel ? root.dashboardModel.weatherIconColor : "#68c8ff"
                            font.pixelSize: 28
                        }
                        Text {
                            text: root.dashboardModel ? root.dashboardModel.weatherSummary.toUpperCase() : "--"
                            color: "#d8ebf8"
                            font.pixelSize: 18
                            font.bold: true
                        }
                    }
                    Text {
                        text: root.dashboardModel ? root.dashboardModel.locationName : ""
                        color: "#d5ebf8"
                        font.pixelSize: 16
                        horizontalAlignment: Text.AlignRight
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
            spacing: 6

            Repeater {
                model: root.dashboardModel ? root.dashboardModel.forecastItems : []
                delegate: Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true

                    Column {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: parent.top
                        spacing: 0

                        Text {
                            text: modelData.day
                            color: "#e6f2ff"
                            font.pixelSize: 22
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Text {
                            text: modelData.icon
                            color: modelData.iconColor
                            font.pixelSize: 30
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Text {
                            text: modelData.high
                            color: "#ffaf8d"
                            font.pixelSize: 18
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Text {
                            text: modelData.low
                            color: "#61d1ff"
                            font.pixelSize: 18
                            font.bold: true
                            horizontalAlignment: Text.AlignHCenter
                        }
                    }
                }
            }
        }
    }
}
