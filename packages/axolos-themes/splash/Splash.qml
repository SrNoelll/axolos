/*
    AxolOS · animación de arranque (KSplash, Plasma 6)
    El ajolote real del fondo entra caminando en la oscuridad con su propia
    luz (pies apoyados de verdad), frena, da un coletazo, abre el ojo y un iris
    de luz enciende el mundo. En 1,9 s; el último fotograma ES el escritorio.
    - Personaje: Axolote.qml   - Tiempos: film.js   - Luz: shaders/mundo.frag
    Todo se dibuja a partir de un único tiempo `t` (determinista).
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Window
import QtQuick.Shapes
import org.kde.kirigami as Kirigami
import "film.js" as Film

Rectangle {
    id: root
    color: "#000000"   // negro puro: los bordes del empuje de cámara no se ven

    property int stage                 // KSplash: 1…6
    property real t: 0                 // tiempo de la película (s)
    property bool autoClock: true      // false = lo fija quien renderiza (storyboard)
    property real exitAt: -1

    readonly property bool reducedMotion: Kirigami.Units.longDuration <= 1
    readonly property real exitP: exitAt < 0 ? 0 : Film.clamp((t - exitAt) / 0.6, 0, 1)
    readonly property var p: Film.pose(t, exitP)
    readonly property var w: Film.world(t, p)
    readonly property var h: Film.hud(t, exitP)

    // El fondo se pinta "escalado y recortado", igual que en el escritorio
    readonly property real wpW: 2730
    readonly property real wpH: 1536
    readonly property real wpScale: Math.max(width / wpW, height / wpH)
    readonly property real wpX: (width - wpW * wpScale) / 2
    readonly property real wpY: (height - wpH * wpScale) / 2
    // Tamaño real en pantalla: las texturas se cargan ya a esta escala (como Plasma)
    readonly property size screenPx: Qt.size(Math.round(width * Screen.devicePixelRatio), Math.round(height * Screen.devicePixelRatio))
    readonly property real px: wpScale * Screen.devicePixelRatio
    // El fondo exacto del escritorio (el PKGBUILD pone la ruta real)
    readonly property string wpFile: "@WALLPAPER@"
    readonly property url wallpaper: wpFile.charAt(0) === "@"
        ? "file:///usr/share/wallpapers/AxolOS/contents/images/2730x1536.jpg" : wpFile

    Component.onCompleted: if (reducedMotion) t = Film.T.end + 1
    onStageChanged: if (reducedMotion && stage >= 5 && exitAt < 0) exitAt = t - 1

    FrameAnimation {
        running: root.autoClock && !root.reducedMotion
        onTriggered: {
            // Siempre a velocidad real (la película dura menos que el arranque medido)
            root.t += frameTime
            if (root.stage >= 5 && root.exitAt < 0 && root.t >= Film.T.end)
                root.exitAt = root.t
        }
    }

    // ---------------------------------------------------------------- cámara
    Item {
        id: camera
        anchors.fill: parent
        transform: Scale {
            origin.x: root.width * 0.46; origin.y: root.height * 0.52
            xScale: root.w.scale; yScale: root.w.scale
        }

        // Mundo (paralaje: se mueve menos que el ajolote)
        Item {
            x: root.wpX + root.w.camX * root.w.parallax * root.wpScale
            y: root.wpY
            width: root.wpW; height: root.wpH
            scale: root.wpScale
            transformOrigin: Item.TopLeft

            Image {
                id: plate; source: "rig/plate.jpg"; visible: false; smooth: true
                sourceSize: Qt.size(Math.round(root.wpW * root.px), Math.round(root.wpH * root.px))
            }
            Image { id: holeMask; source: "rig/hole.png"; visible: false; smooth: true }
            ShaderEffect {
                width: root.wpW; height: root.wpH
                fragmentShader: Qt.resolvedUrl("shaders/mundo.frag.qsb")
                property var source: plate
                property var hole: holeMask
                property real lightX: (Film.CENTER[0] + root.p.bodyX + root.w.camX * (1 - root.w.parallax)) / root.wpW
                property real lightY: (Film.CENTER[1] + root.p.bodyY) / root.wpH
                property real lightI: root.w.lightI
                property real eyeX: Film.EYE[0] / root.wpW
                property real eyeY: Film.EYE[1] / root.wpH
                property real iris: root.w.iris
                property real aspect: root.wpW / root.wpH
            }
        }

        // Actor (su propia luz lo enciende al empezar)
        Item {
            opacity: root.w.key
            x: root.wpX + root.w.camX * root.wpScale
            y: root.wpY
            width: root.wpW; height: root.wpH
            scale: root.wpScale
            transformOrigin: Item.TopLeft

            Axolote {
                pixelScale: root.px
                legFL: root.p.legFL; legFR: root.p.legFR
                legBL: root.p.legBL; legBR: root.p.legBR
                tail: root.p.tail
                bodyRot: root.p.bodyRot
                bodyX: root.p.bodyX; bodyY: root.p.bodyY
            }

        }
    }

    // ---------------------------------------------------------------- escritorio exacto
    // Cuando el iris termina, el ajolote está en su pose de reposo al píxel: a
    // partir de ahí se dibuja el fondo EXACTAMENTE como lo dibuja Plasma (misma
    // imagen, mismo recorte, misma escala). Al cerrarse KSplash no cambia nada.
    Image {
        anchors.fill: parent
        source: root.wallpaper
        fillMode: Image.PreserveAspectCrop
        sourceSize: root.screenPx
        asynchronous: true
        opacity: status === Image.Ready ? root.w.desk : 0
        visible: opacity > 0
    }

    // Destello del ojo (por encima de todo; la cámara ya está en 1:1 cuando ocurre)
    Item {
        x: root.wpX; y: root.wpY
        width: root.wpW; height: root.wpH
        scale: root.wpScale
        transformOrigin: Item.TopLeft
        // Destello del ojo: abre el ojo justo antes del iris de luz
        Shape {
            x: Film.EYE[0] + root.p.bodyX - 70; y: Film.EYE[1] + root.p.bodyY - 70
            width: 140; height: 140
            opacity: root.w.glint
            visible: opacity > 0.001
            preferredRendererType: Shape.CurveRenderer
            ShapePath {
                strokeWidth: -1
                fillGradient: RadialGradient {
                centerX: 70; centerY: 70; focalX: 70; focalY: 70; centerRadius: 70
                GradientStop { position: 0.00; color: "#ffffffff" }
                GradientStop { position: 0.12; color: "#f0e8e8ee" }
                GradientStop { position: 0.35; color: "#40e8e8ee" }
                GradientStop { position: 1.00; color: "#00e8e8ee" }
                }
                PathAngleArc { centerX: 70; centerY: 70; radiusX: 70; radiusY: 70; startAngle: 0; sweepAngle: 360 }
            }
        }
    }

    // ---------------------------------------------------------------- marca
    Item {
        id: hud
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.rightMargin: Math.round(root.height * 0.055)
        anchors.bottomMargin: Math.round(root.height * 0.06)
        width: Math.round(root.height * 0.30)
        height: Math.round(root.height * 0.092)
        visible: root.h.open > 0.001

        Rectangle {                       // tarjeta: se despliega de izquierda a derecha
            width: parent.width * root.h.open
            height: parent.height
            radius: Math.round(root.height * 0.012)
            color: "#c4050506"
            border.color: "#2a2a30"; border.width: 1
            clip: true

            Text {
                x: Math.round(root.height * 0.022); y: Math.round(root.height * 0.010)
                text: "AxolOS"
                color: "#e8e8ee"
                font.family: "New York Extra Large"
                font.pixelSize: Math.round(root.height * 0.036)
            }
            Text {
                readonly property string full: "arrancando · " + Math.max(1, Math.min(6, root.stage)) + "/6"
                x: Math.round(root.height * 0.024); y: Math.round(root.height * 0.058)
                text: full.substring(0, root.h.typed)
                color: "#a3a3ab"
                font.family: "iA Writer Mono S"
                font.pixelSize: Math.round(root.height * 0.0145)
            }
            Rectangle {                   // progreso: el único violeta
                anchors.bottom: parent.bottom
                height: Math.max(2, Math.round(root.height * 0.0025))
                width: parent.width * Math.min(1, Math.max(0, root.stage) / 6)
                color: "#926ee4"
                Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
            }
        }
    }
}
