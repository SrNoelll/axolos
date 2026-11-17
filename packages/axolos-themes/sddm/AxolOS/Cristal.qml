/*
    AxolOS · cristal líquido real para QtQuick: refracta y separa en colores lo que hay detrás.
    Las texturas de la escena (nítida y desenfocada) se crean una vez en Main.qml y se comparten.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick

ShaderEffect {
    id: cristal
    required property Item escena          // el elemento que ocupa la escena entera (coordenadas)
    required property var nitido           // texturas compartidas de la escena
    required property var borroso
    property real radio: 26
    property real bisel: 22
    property real fuerza: 26
    property real dispersion: 0.22
    property color tinte: Qt.rgba(0.07, 0.07, 0.09, 0.30)
    property real brillo: 1.0

    property size tam: Qt.size(width, height)
    property rect zona: Qt.rect(0, 0, 1, 1)
    function recolocar() {
        if (!escena || escena.width <= 0 || escena.height <= 0)
            return
        const q = mapToItem(escena, 0, 0)
        zona = Qt.rect(q.x / escena.width, q.y / escena.height, width / escena.width, height / escena.height)
    }
    onWidthChanged: recolocar()
    onHeightChanged: recolocar()
    onXChanged: recolocar()
    onYChanged: recolocar()
    Component.onCompleted: recolocar()
    Timer { interval: 250; running: true; onTriggered: cristal.recolocar() }   // tras colocar los layouts

    fragmentShader: "cristal.frag.qsb"
}
