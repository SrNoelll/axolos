// Puerta 1 · Hoja de personaje del ajolote AxolOS (renderizada desde Axolote.qml)
// Uso: tools/splash-dev/render.sh hoja <salida.png>
import QtQuick
import QtQuick.Window
import "../../packages/axolos-themes/splash"

Window {
    id: win
    width: 1920; height: 1080; visible: true
    color: "#0b0b0e"
    readonly property string out: Qt.application.arguments[Qt.application.arguments.length - 1]

    readonly property string display: "New York Extra Large"
    readonly property string mono: "iA Writer Mono S"
    readonly property var palette: [
        ["Abismo", "#050506", "fondo"], ["Obsidiana", "#121215", "tubos"],
        ["Grafito", "#2a2a30", "sombra"], ["Hierro", "#5b5b63", "cuerpo"],
        ["Plata", "#a3a3ab", "luz"], ["Destello", "#e8e8ee", "filo"],
        ["Violeta AxolOS", "#926ee4", "solo interfaz"]
    ]
    // 5 poses = las "expresiones" del personaje
    readonly property var poses: [
        { t: "Reposo", d: "la pose del fondo, al píxel", p: {} },
        { t: "Paso A", d: "diagonal izq.-del. + tras.-der.", p: { legFL: 14, legBR: 12, legFR: -11, legBL: -10, tail: -1.5, bodyRot: -1.2, bodyY: -10 } },
        { t: "Paso B", d: "la diagonal contraria", p: { legFL: -11, legBR: -10, legFR: 14, legBL: 12, tail: 1.5, bodyRot: 1.2, bodyY: -10 } },
        { t: "Anticipación", d: "se echa atrás antes de frenar", p: { legFL: 10, legFR: 9, legBL: -9, legBR: -9, bodyRot: 1.8, bodyX: 30, tail: -2 } },
        { t: "Coletazo", d: "llega, planta y sacude la cola", p: { legFR: -6, tail: 3.2, bodyRot: -0.8 } }
    ]

    // ---- Cabecera ----
    Text {
        x: 64; y: 40
        text: "Ajolote · hoja de personaje"
        color: "#e8e8ee"; font.family: win.display; font.pixelSize: 52
    }
    Text {
        x: 66; y: 112
        text: "AxolOS · animación de arranque · puerta 1 de 4"
        color: "#8a8a94"; font.family: win.mono; font.pixelSize: 18
    }

    // ---- Rig explosionado ----
    Rectangle {
        id: rigCard
        x: 64; y: 160; width: 1080; height: 565; radius: 18
        color: "#050506"; border.color: "#1e1e24"
        clip: true
        Axolote {
            id: exploded
            explode: 0.7; showPivots: true
            transformOrigin: Item.TopLeft
            scale: 0.385
            x: -296 * scale + 140; y: -72 * scale + 40
        }
        Text {
            x: 24; y: 20; text: "RIG · 6 piezas, 5 pivotes"
            color: "#a3a3ab"; font.family: win.mono; font.pixelSize: 16; font.letterSpacing: 2
        }
        Column {
            x: 24; anchors.bottom: parent.bottom; anchors.bottomMargin: 20; spacing: 4
            Repeater {
                model: ["cuerpo · rígido: cabeza, branquias y lomo",
                        "4 patas · pivote en hombro / cadera · ±14°",
                        "cola · pivote en la base · ±3°",
                        "articulaciones rellenas: no se ve hueco al girar"]
                Text { required property string modelData; text: modelData; color: "#8a8a94"; font.family: win.mono; font.pixelSize: 15 }
            }
        }
    }

    // ---- Paleta ----
    Text { x: 1190; y: 160; text: "PALETA"; color: "#a3a3ab"; font.family: win.mono; font.pixelSize: 16; font.letterSpacing: 2 }
    Grid {
        x: 1190; y: 192; columns: 2; columnSpacing: 26; rowSpacing: 10
        Repeater {
            model: win.palette
            Row {
                required property var modelData
                spacing: 12; width: 320
                Rectangle { width: 48; height: 34; radius: 7; color: modelData[1]; border.color: "#2a2a30" }
                Column {
                    anchors.verticalCenter: parent.verticalCenter
                    Text { text: modelData[0]; color: "#e8e8ee"; font.family: win.display; font.pixelSize: 18 }
                    Text { text: modelData[1] + " · " + modelData[2]; color: "#8a8a94"; font.family: win.mono; font.pixelSize: 12 }
                }
            }
        }
    }

    // ---- Tipografía y luz ----
    Text { x: 1190; y: 395; text: "TIPOGRAFÍA"; color: "#a3a3ab"; font.family: win.mono; font.pixelSize: 16; font.letterSpacing: 2 }
    Text { x: 1186; y: 412; text: "AxolOS"; color: "#e8e8ee"; font.family: win.display; font.pixelSize: 60 }
    Text { x: 1190; y: 488; text: "New York Extra Large · display"; color: "#8a8a94"; font.family: win.mono; font.pixelSize: 12 }
    Text { x: 1440; y: 436; text: "arrancando · 3/6"; color: "#c9c9d1"; font.family: win.mono; font.pixelSize: 22 }
    Text { x: 1440; y: 488; text: "iA Writer Mono S · texto"; color: "#8a8a94"; font.family: win.mono; font.pixelSize: 12 }
    Text { x: 1720; y: 395; text: "LUZ"; color: "#a3a3ab"; font.family: win.mono; font.pixelSize: 16; font.letterSpacing: 2 }
    Item {
        x: 1720; y: 425; width: 130; height: 80
        Rectangle { x: 40; y: 26; width: 70; height: 46; radius: 23; color: "#000000"; opacity: 0.9 }
        Rectangle {
            x: 30; y: 16; width: 70; height: 46; radius: 23
            gradient: Gradient { GradientStop { position: 0; color: "#a3a3ab" } GradientStop { position: 1; color: "#2a2a30" } }
        }
        Text { x: 0; y: -4; text: "↘"; color: "#e8e8ee"; font.pixelSize: 26 }
    }

    // ---- 5 poses ----
    Row {
        x: 64; y: 748; spacing: 16
        Repeater {
            model: win.poses
            Rectangle {
                id: card
                required property var modelData
                width: 345; height: 300; radius: 16
                color: "#050506"; border.color: "#1e1e24"; clip: true
                Axolote {
                    transformOrigin: Item.TopLeft
                    scale: 0.15
                    x: -296 * scale + 30; y: -72 * scale + 18
                    legFL: card.modelData.p.legFL || 0; legFR: card.modelData.p.legFR || 0
                    legBL: card.modelData.p.legBL || 0; legBR: card.modelData.p.legBR || 0
                    tail: card.modelData.p.tail || 0; bodyRot: card.modelData.p.bodyRot || 0
                    bodyX: card.modelData.p.bodyX || 0; bodyY: card.modelData.p.bodyY || 0
                }
                Text { x: 18; y: 238; text: card.modelData.t; color: "#e8e8ee"; font.family: win.display; font.pixelSize: 24 }
                Text { x: 18; y: 270; text: card.modelData.d; color: "#8a8a94"; font.family: win.mono; font.pixelSize: 13 }
            }
        }
    }

    // ---- Reglas del personaje ----
    Column {
        x: 1190; y: 528; spacing: 6; width: 666
        Text { text: "REGLAS"; color: "#a3a3ab"; font.family: win.mono; font.pixelSize: 16; font.letterSpacing: 2 }
        Repeater {
            model: [
                "1. Siempre es el ajolote real del fondo. No se redibuja ni se deforma: solo giran sus piezas.",
                "2. Mira a la izquierda y avanza hacia donde mira. Peso lento: un paso cada 0,5 s.",
                "3. Giros pequeños: patas ±14°, cola ±3°, cuerpo ±2°. Anticipa antes de frenar; se pasa un poco y se asienta.",
                "4. Luz clave arriba-izquierda, sombra abajo-derecha. El violeta es solo de la interfaz, nunca del ajolote.",
                "5. Termina en la pose del fondo, al píxel: la última imagen del splash es el escritorio."
            ]
            Text { required property string modelData; width: 666; wrapMode: Text.WordWrap; text: modelData; color: "#c9c9d1"; font.family: win.mono; font.pixelSize: 13; lineHeight: 1.1 }
        }
    }

    Timer {
        interval: 2500; running: true
        onTriggered: win.contentItem.grabToImage(function (r) { r.saveToFile(win.out); Qt.quit() })
    }
}
