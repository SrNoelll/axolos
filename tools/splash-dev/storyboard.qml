// Puerta 2 · Storyboard: 9 fotogramas clave renderizados desde la película real.
// También sirve para el borrador (modo "draft": todos los fotogramas a 30 fps).
import QtQuick
import QtQuick.Window
import "../../packages/axolos-themes/splash"

Window {
    id: win
    width: 1920; height: 1080; visible: true; color: "black"
    readonly property var args: Qt.application.arguments
    readonly property string outDir: args[args.length - 1]
    readonly property string mode: args[args.length - 2]      // "storyboard" | "draft"
    readonly property var keys: [0.06, 0.12, 0.40, 0.78, 1.12, 1.30, 1.35, 1.62, 2.30]
    readonly property var times: {
        if (mode === "storyboard") return keys
        if (mode.indexOf("t=") === 0) return [parseFloat(mode.substring(2))]
        var a = []; for (var i = 0; i < 3.0 * 30; i++) a.push(i / 30); return a
    }
    property int i: 0

    // Etapas de KSplash simuladas en función del tiempo (como un arranque real)
    function stageAt(t) { return t < 0.35 ? 1 : t < 0.7 ? 2 : t < 1.05 ? 3 : t < 1.4 ? 4 : t < 1.8 ? 5 : 6 }

    Splash {
        id: film
        anchors.fill: parent
        autoClock: false
        t: win.times[win.i]
        stage: win.stageAt(t)
        exitAt: -1
        // a partir del cierre real de KSplash se ve TU escritorio de verdad (el fondo)
        Image {
            anchors.fill: parent
            visible: film.t >= win.closeAt
            source: "file:///usr/share/wallpapers/AxolOS/contents/images/2730x1536.jpg"
            fillMode: Image.PreserveAspectCrop
            sourceSize: Qt.size(1920, 1080)          // igual que Plasma (org.kde.image)
            z: 100
        }
    }

    readonly property real closeAt: 2.14   // cierre real de KSplash medido en este equipo
    function pad(n) { return ("0000" + n).slice(-4) }
    Timer {
        id: tick
        interval: win.i === 0 ? 1500 : 60; running: true
        onTriggered: film.grabToImage(function (r) {
            r.saveToFile(win.outDir + "/f-" + win.pad(win.i) + ".png")
            if (win.i + 1 >= win.times.length) { Qt.quit(); return }
            win.i++
            tick.restart()
        }, win.mode === "draft" ? Qt.size(960, 540) : win.mode === "final" ? Qt.size(1920, 1080) : win.mode.indexOf("t=") === 0 ? Qt.size(1920, 1080) : Qt.size(1280, 720))
    }
}
