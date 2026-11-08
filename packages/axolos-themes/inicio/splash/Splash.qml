/*
    AxolOS · animación de inicio de Plasma (KSplash)
    El final del vídeo del ajolote, a velocidad real (24 fps), terminando en la
    pose exacta de tu fondo. KSplash vive en pantalla lo que tarda Plasma en
    cargar el escritorio (~1,1 s en tu portátil), así que:
      · el reloj NO arranca al cargar el QML sino cuando esta pantalla pinta
        su primer fotograma de verdad (antes estaría corriendo a oscuras);
      · cada pantalla (portátil, HDMI...) arranca con su propio primer fotograma;
      · si Plasma tarda más, se queda quieto en la pose del fondo.
    Deja en el registro (journalctl --user -t ksplashqml) cuándo se vio y cuándo
    se cerró, para medirlo en un arranque real.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Window

Rectangle {
    id: root
    color: "black"
    property int stage

    readonly property int first: 26          // f26 … f49: el último segundo
    readonly property int last: 49           // f49 = pose del fondo
    readonly property int count: last - first + 1
    property real frame: 0
    readonly property int shown: first + Math.min(count - 1, Math.floor(frame))

    readonly property double t0: Date.now()
    property double tVisible: 0

    function src(i) { return "images/frames/f" + (i < 10 ? "0" : "") + i + ".jpg" }

    // fotograma actual (síncrono: nunca queda un hueco al cambiar)
    Image {
        anchors.fill: parent
        source: root.src(root.shown)
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
        cache: true
        smooth: true
    }
    // el siguiente, ya decodificado y escondido: el cambio es inmediato
    Image {
        visible: false
        source: root.src(Math.min(root.last, root.shown + 1))
        asynchronous: true
        cache: true
    }

    NumberAnimation {
        id: play
        target: root; property: "frame"
        from: 0; to: root.count
        duration: Math.round(root.count * 1000 / 24)      // 1,0 s, a ritmo de reloj
    }

    // primer fotograma realmente presentado en esta pantalla → empieza
    Connections {
        target: root.Window.window
        enabled: root.tVisible === 0
        function onFrameSwapped() {
            root.tVisible = Date.now()
            play.start()
            console.info("AxolOS splash: visible en", root.Screen.name,
                         "a los", root.tVisible - root.t0, "ms de cargar")
        }
    }

    onStageChanged: console.info("AxolOS splash: etapa", stage, "en",
                                 root.Screen.name,
                                 "· visible desde hace", root.tVisible ? Date.now() - root.tVisible : -1, "ms")
}
