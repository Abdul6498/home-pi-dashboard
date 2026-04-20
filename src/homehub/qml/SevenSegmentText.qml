import QtQuick

Row {
    id: root
    property string value: "00:00"
    property color activeColor: "#f4f7fb"
    property color inactiveColor: "#16303b"
    property real glyphWidth: 54
    property real glyphHeight: 96
    property real glyphSpacing: 6

    spacing: glyphSpacing

    Repeater {
        model: root.value.length

        delegate: SevenSegmentGlyph {
            character: root.value[index]
            activeColor: root.activeColor
            inactiveColor: root.inactiveColor
            width: character === ":" ? Math.max(12, root.glyphWidth * 0.32) : root.glyphWidth
            height: root.glyphHeight
        }
    }
}
