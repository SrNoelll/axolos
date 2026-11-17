/*
    AxolOS · pantalla de inicio de Plasma (KSplash)
    El fondo de cristal líquido, tal cual: Plasma tarda ~1 s en cargar el escritorio y el primer
    fotograma del escritorio es exactamente esta imagen, así que el paso es invisible.
    (La animación del ajolote metálico terminaba en la pose del fondo anterior; la del ajolote de
    cristal se hará aparte.)
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick

Rectangle {
    id: root
    color: "black"
    property int stage

    Image {
        anchors.fill: parent
        source: "images/fondo.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        smooth: true
    }

    onStageChanged: console.info("AxolOS splash: etapa", stage, "en", root.Screen.name)
}
