import QtQuick

Item {
    id: root
    property string kind: "cloudy"
    property color primaryColor: "#68c8ff"
    property color secondaryColor: "#dff1ff"

    implicitWidth: 36
    implicitHeight: 28

    Canvas {
        id: iconCanvas
        anchors.fill: parent
        antialiasing: true

        onPaint: {
            const ctx = getContext("2d")
            const w = width
            const h = height

            function reset() {
                ctx.reset()
                ctx.clearRect(0, 0, w, h)
                ctx.lineCap = "round"
                ctx.lineJoin = "round"
            }

            function drawCloud(x, y, scale, fill) {
                const baseW = 18 * scale
                const baseH = 8 * scale
                ctx.fillStyle = fill
                ctx.beginPath()
                ctx.arc(x + 5 * scale, y + 7 * scale, 4 * scale, Math.PI, 2 * Math.PI)
                ctx.arc(x + 11 * scale, y + 5 * scale, 5 * scale, Math.PI, 2 * Math.PI)
                ctx.arc(x + 17 * scale, y + 7 * scale, 4 * scale, Math.PI, 2 * Math.PI)
                ctx.closePath()
                ctx.fill()
                ctx.fillRect(x + 4 * scale, y + 7 * scale, baseW, baseH)
            }

            function drawSun(cx, cy, r, fill) {
                ctx.strokeStyle = fill
                ctx.fillStyle = fill
                ctx.lineWidth = Math.max(1.2, r * 0.18)
                for (let i = 0; i < 8; i++) {
                    const angle = (Math.PI * 2 * i) / 8
                    const inner = r + 2
                    const outer = r + 6
                    ctx.beginPath()
                    ctx.moveTo(cx + Math.cos(angle) * inner, cy + Math.sin(angle) * inner)
                    ctx.lineTo(cx + Math.cos(angle) * outer, cy + Math.sin(angle) * outer)
                    ctx.stroke()
                }
                ctx.beginPath()
                ctx.arc(cx, cy, r, 0, Math.PI * 2)
                ctx.fill()
            }

            function drawRain(x, y, fill) {
                ctx.strokeStyle = fill
                ctx.lineWidth = 1.7
                for (let i = 0; i < 3; i++) {
                    const dx = x + i * 6
                    ctx.beginPath()
                    ctx.moveTo(dx, y)
                    ctx.lineTo(dx - 1.5, y + 6)
                    ctx.stroke()
                }
            }

            function drawSnow(x, y, fill) {
                ctx.strokeStyle = fill
                ctx.lineWidth = 1.4
                const cx = x
                const cy = y
                const r = 4
                for (let i = 0; i < 3; i++) {
                    const angle = i * Math.PI / 3
                    ctx.beginPath()
                    ctx.moveTo(cx - Math.cos(angle) * r, cy - Math.sin(angle) * r)
                    ctx.lineTo(cx + Math.cos(angle) * r, cy + Math.sin(angle) * r)
                    ctx.stroke()
                }
            }

            function drawFog(fill) {
                ctx.strokeStyle = fill
                ctx.lineWidth = 2
                for (let i = 0; i < 3; i++) {
                    const y = 8 + i * 6
                    ctx.beginPath()
                    ctx.moveTo(6, y)
                    ctx.lineTo(w - 6, y)
                    ctx.stroke()
                }
            }

            function drawLightning(fill) {
                ctx.fillStyle = fill
                ctx.beginPath()
                ctx.moveTo(19, 12)
                ctx.lineTo(13, 22)
                ctx.lineTo(18, 22)
                ctx.lineTo(14, 30)
                ctx.lineTo(24, 17)
                ctx.lineTo(18, 17)
                ctx.closePath()
                ctx.fill()
            }

            reset()

            if (root.kind === "clear") {
                drawSun(w * 0.5, h * 0.48, Math.min(w, h) * 0.22, root.primaryColor)
                return
            }

            if (root.kind === "partly_cloudy") {
                drawSun(w * 0.34, h * 0.36, Math.min(w, h) * 0.18, "#ffd34d")
                drawCloud(w * 0.24, h * 0.30, Math.min(w, h) / 28, root.secondaryColor)
                return
            }

            if (root.kind === "cloudy") {
                drawCloud(w * 0.2, h * 0.28, Math.min(w, h) / 26, root.primaryColor)
                return
            }

            if (root.kind === "rainy") {
                drawCloud(w * 0.2, h * 0.22, Math.min(w, h) / 26, root.primaryColor)
                drawRain(w * 0.42, h * 0.72, root.secondaryColor)
                return
            }

            if (root.kind === "snowy") {
                drawCloud(w * 0.2, h * 0.22, Math.min(w, h) / 26, root.primaryColor)
                drawSnow(w * 0.50, h * 0.76, root.secondaryColor)
                return
            }

            if (root.kind === "storm") {
                drawCloud(w * 0.2, h * 0.18, Math.min(w, h) / 26, root.primaryColor)
                drawLightning("#ffd34d")
                return
            }

            if (root.kind === "fog") {
                drawFog(root.primaryColor)
                return
            }

            drawCloud(w * 0.2, h * 0.28, Math.min(w, h) / 26, root.primaryColor)
        }

        Connections {
            target: root
            function onKindChanged() { iconCanvas.requestPaint() }
            function onPrimaryColorChanged() { iconCanvas.requestPaint() }
            function onSecondaryColorChanged() { iconCanvas.requestPaint() }
        }
    }
}
