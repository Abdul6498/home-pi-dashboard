import QtQuick

Item {
    id: root
    property string character: "0"
    property color activeColor: "#f4f7fb"
    property color inactiveColor: "#16303b"
    property real segmentThickness: Math.max(3, width * 0.16)
    property real horizontalLength: Math.max(4, width - segmentThickness * 1.8)
    property real verticalLength: Math.max(4, (height - segmentThickness * 3.1) / 2)

    implicitWidth: character === ":" ? 18 : 54
    implicitHeight: 96

    function segmentOn(name) {
        const digitMap = {
            "0": ["a", "b", "c", "d", "e", "f"],
            "1": ["b", "c"],
            "2": ["a", "b", "g", "e", "d"],
            "3": ["a", "b", "g", "c", "d"],
            "4": ["f", "g", "b", "c"],
            "5": ["a", "f", "g", "c", "d"],
            "6": ["a", "f", "g", "e", "c", "d"],
            "7": ["a", "b", "c"],
            "8": ["a", "b", "c", "d", "e", "f", "g"],
            "9": ["a", "b", "c", "d", "f", "g"],
            "-": ["g"]
        }
        const active = digitMap[character] || []
        return active.indexOf(name) !== -1
    }

    Rectangle {
        visible: root.character !== ":"
        x: root.segmentThickness
        y: 0
        width: root.horizontalLength
        height: root.segmentThickness
        radius: root.segmentThickness / 2
        color: root.segmentOn("a") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: root.width - root.segmentThickness
        y: root.segmentThickness * 0.75
        width: root.segmentThickness
        height: root.verticalLength
        radius: root.segmentThickness / 2
        color: root.segmentOn("b") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: root.width - root.segmentThickness
        y: root.segmentThickness * 1.65 + root.verticalLength
        width: root.segmentThickness
        height: root.verticalLength
        radius: root.segmentThickness / 2
        color: root.segmentOn("c") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: root.segmentThickness
        y: root.height - root.segmentThickness
        width: root.horizontalLength
        height: root.segmentThickness
        radius: root.segmentThickness / 2
        color: root.segmentOn("d") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: 0
        y: root.segmentThickness * 1.65 + root.verticalLength
        width: root.segmentThickness
        height: root.verticalLength
        radius: root.segmentThickness / 2
        color: root.segmentOn("e") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: 0
        y: root.segmentThickness * 0.75
        width: root.segmentThickness
        height: root.verticalLength
        radius: root.segmentThickness / 2
        color: root.segmentOn("f") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character !== ":"
        x: root.segmentThickness
        y: (root.height - root.segmentThickness) / 2
        width: root.horizontalLength
        height: root.segmentThickness
        radius: root.segmentThickness / 2
        color: root.segmentOn("g") ? root.activeColor : root.inactiveColor
    }

    Rectangle {
        visible: root.character === ":"
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.height * 0.28
        width: root.segmentThickness
        height: root.segmentThickness
        radius: width / 2
        color: root.activeColor
    }

    Rectangle {
        visible: root.character === ":"
        anchors.horizontalCenter: parent.horizontalCenter
        y: root.height * 0.62
        width: root.segmentThickness
        height: root.segmentThickness
        radius: width / 2
        color: root.activeColor
    }
}
