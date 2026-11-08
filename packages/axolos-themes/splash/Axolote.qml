/*
    AxolOS · personaje: el ajolote REAL del fondo, articulado por piezas.
    Vive en coordenadas del fondo (2730x1536 px): en reposo coincide al píxel
    con el ajolote del escritorio. Nunca se deforma; solo giran las piezas.
    Las piezas y pivotes salen de tools/rig_axolote.py (rig/rig.js).
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import "rig/rig.js" as R

Item {
    id: ax
    width: R.RIG.wallpaper[0]
    height: R.RIG.wallpaper[1]

    // ---- Pose (grados y px del fondo) ----
    property real legFL: 0      // pata delantera izquierda  (+ = hacia delante)
    property real legFR: 0      // pata delantera derecha
    property real legBL: 0      // pata trasera izquierda
    property real legBR: 0      // pata trasera derecha
    property real tail: 0       // cola (+ = la punta baja)
    property real bodyRot: 0    // balanceo del cuerpo entero
    property real bodyX: 0
    property real bodyY: 0
    // ---- Solo para la hoja de personaje ----
    property real pixelScale: 1     // escala final en pantalla: la textura se carga ya a ese tamaño
    property real explode: 0
    property bool showPivots: false

    readonly property real cx: R.RIG.axolotl[0] + R.RIG.axolotl[2] / 2
    readonly property real cy: R.RIG.axolotl[1] + R.RIG.axolotl[3] / 2

    function angleFor(name) {
        switch (name) {
        case "leg_fl": return legFL
        case "leg_fr": return legFR
        case "leg_bl": return legBL
        case "leg_br": return legBR
        case "tail":   return tail
        }
        return 0
    }
    function offset(l, axis) {          // vista explosionada
        if (!l.pivot || explode === 0) return 0
        return (axis === 0 ? l.pivot[0] - cx : l.pivot[1] - cy) * 0.35 * explode
    }

    Item {
        id: body
        width: ax.width; height: ax.height
        transform: [
            Rotation { origin.x: ax.cx; origin.y: ax.cy; angle: ax.bodyRot },
            Translate { x: ax.bodyX; y: ax.bodyY }
        ]
        Repeater {
            model: R.RIG.layers
            delegate: Item {
                id: part
                required property var modelData
                x: modelData.x + ax.offset(modelData, 0)
                y: modelData.y + ax.offset(modelData, 1)
                width: modelData.w; height: modelData.h
                z: modelData.z
                Image {
                    anchors.fill: parent
                    source: "rig/" + part.modelData.name + ".png"
                    smooth: true
                    asynchronous: false
                    sourceSize: Qt.size(Math.round(part.modelData.w * ax.pixelScale),
                                        Math.round(part.modelData.h * ax.pixelScale))
                    transform: Rotation {
                        origin.x: part.modelData.pivot ? part.modelData.pivot[0] - part.modelData.x : 0
                        origin.y: part.modelData.pivot ? part.modelData.pivot[1] - part.modelData.y : 0
                        angle: ax.angleFor(part.modelData.name)
                    }
                }
                Rectangle {                    // pivote (hoja de personaje)
                    visible: ax.showPivots && !!part.modelData.pivot
                    width: 26; height: 26; radius: 13
                    color: "#926ee4"; border.color: "#e8e8ee"; border.width: 4
                    x: (part.modelData.pivot ? part.modelData.pivot[0] - part.modelData.x : 0) - 13
                    y: (part.modelData.pivot ? part.modelData.pivot[1] - part.modelData.y : 0) - 13
                    z: 10
                }
            }
        }
    }
}
