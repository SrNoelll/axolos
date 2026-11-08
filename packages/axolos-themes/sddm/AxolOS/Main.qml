/*
    AxolOS · pantalla de inicio de sesión (SDDM, Qt 6)
    Tu fondo, un reloj grande, y una tarjeta de cristal con el avatar del
    ajolote y la contraseña. Paleta y tipografías de AxolOS.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import QtQuick.Effects

Rectangle {
    id: root
    width: 1920; height: 1080
    color: "#050506"

    readonly property color cText: "#ececf1"
    readonly property color cMuted: "#a3a3ae"
    readonly property color cAccent: config.accent || "#a69afe"
    readonly property string fDisplay: "New York Extra Large"
    readonly property string fUi: "SF Pro Display"
    readonly property string fMono: "iA Writer Mono S"

    property int userIndex: userModel.lastIndex >= 0 ? userModel.lastIndex : 0
    property int sessionIndex: sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property var now: new Date()
    readonly property var dias: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    readonly property var meses: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                  "septiembre", "octubre", "noviembre", "diciembre"]
    function two(n) { return (n < 10 ? "0" : "") + n }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

    // ---- fondo -------------------------------------------------------------------
    Image {
        id: bg
        anchors.fill: parent
        source: config.background || "/usr/share/wallpapers/AxolOS/contents/images/2730x1536.jpg"
        fillMode: Image.PreserveAspectCrop
        asynchronous: false
    }
    Rectangle {                       // velo para que el texto se lea siempre
        anchors.fill: parent
        gradient: Gradient {
            orientation: Gradient.Horizontal
            GradientStop { position: 0.0; color: "#b0050506" }
            GradientStop { position: 0.55; color: "#40050506" }
            GradientStop { position: 1.0; color: "#10050506" }
        }
    }

    // ---- reloj ---------------------------------------------------------------------
    Column {
        x: Math.round(root.width * 0.07); y: Math.round(root.height * 0.12)
        spacing: 4
        Text {
            text: root.two(root.now.getHours()) + ":" + root.two(root.now.getMinutes())
            color: root.cText; font.family: root.fDisplay; font.pixelSize: Math.round(root.height * 0.13)
        }
        Text {
            leftPadding: 6
            text: root.dias[root.now.getDay()] + ", " + root.now.getDate() + " de " + root.meses[root.now.getMonth()]
            color: root.cMuted; font.family: root.fUi; font.pixelSize: Math.round(root.height * 0.024)
        }
    }

    // ---- tarjeta de acceso ---------------------------------------------------------
    Item {
        id: card
        width: 400; height: 214
        x: Math.round(root.width * 0.07); y: Math.round(root.height * 0.52)

        // cristal: fondo desenfocado recortado a la tarjeta
        Item {
            anchors.fill: parent
            clip: true
            layer.enabled: true
            layer.effect: MultiEffect {
                maskEnabled: true
                maskSource: ShaderEffectSource { sourceItem: Rectangle { width: card.width; height: card.height; radius: 26 } }
            }
            MultiEffect {
                x: -card.x; y: -card.y
                width: root.width; height: root.height
                source: bg
                blurEnabled: true; blur: 1.0; blurMax: 64
                brightness: -0.25
            }
        }
        Rectangle {
            anchors.fill: parent
            radius: 26
            color: "#a6141418"
            border.color: "#1fffffff"
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 28
            spacing: 14

            RowLayout {
                spacing: 16
                Rectangle {
                    Layout.preferredWidth: 64; Layout.preferredHeight: 64
                    radius: 32; color: "#1d1b2a"; border.color: root.cAccent; border.width: 2
                    Item {                               // foto recortada en círculo de verdad
                        anchors.fill: parent; anchors.margins: 3
                        Image {
                            id: face
                            anchors.fill: parent
                            source: userList.currentItem && userList.currentItem.icon ? userList.currentItem.icon : "avatar.png"
                            fillMode: Image.PreserveAspectCrop
                            visible: false
                            layer.enabled: true
                            onStatusChanged: if (status === Image.Error) source = "avatar.png"
                        }
                        Rectangle { id: faceMask; anchors.fill: parent; radius: width / 2; visible: false; layer.enabled: true }
                        MultiEffect {
                            anchors.fill: parent; source: face
                            maskEnabled: true; maskSource: faceMask
                            maskThresholdMin: 0.5; maskSpreadAtMin: 1.0
                        }
                    }
                }
                ColumnLayout {
                    spacing: 2
                    Text {
                        text: userList.currentItem ? userList.currentItem.display : ""
                        color: root.cText; font.family: root.fDisplay; font.pixelSize: 26
                    }
                    Text {
                        text: sddm.hostName ? "AxolOS · " + sddm.hostName : "AxolOS"
                        color: root.cMuted; font.family: root.fMono; font.pixelSize: 12
                    }
                }
            }

            // usuarios (oculto: se usa para leer nombre/avatar; con varios, flechas ‹ ›)
            ListView {
                id: userList
                Layout.preferredWidth: 1; Layout.preferredHeight: 1
                opacity: 0                          // invisible, pero con tamaño para que cree los elementos
                model: userModel
                currentIndex: root.userIndex
                delegate: Item {
                    required property string name
                    required property string realName
                    required property string icon
                    readonly property string base: realName.length ? realName : name
                    readonly property string display: base.charAt(0).toUpperCase() + base.slice(1)
                    property string login: name
                }
            }

            Rectangle {
                id: field
                Layout.fillWidth: true; Layout.preferredHeight: 48
                radius: 16
                color: "#14ffffff"
                border.color: password.activeFocus ? root.cAccent : "#26ffffff"
                border.width: password.activeFocus ? 1.5 : 1
                TextInput {
                    id: password
                    anchors.fill: parent; anchors.leftMargin: 18; anchors.rightMargin: 52
                    verticalAlignment: TextInput.AlignVCenter
                    echoMode: TextInput.Password
                    passwordCharacter: "•"
                    color: root.cText
                    font.family: root.fUi; font.pixelSize: 16; font.letterSpacing: 2
                    selectionColor: "#7662ce"
                    focus: true
                    clip: true
                    Keys.onReturnPressed: root.doLogin()
                    Keys.onEnterPressed: root.doLogin()
                    Text {
                        anchors.verticalCenter: parent.verticalCenter
                        visible: !password.text.length
                        text: "Contraseña"
                        color: root.cMuted; font.family: root.fUi; font.pixelSize: 15
                    }
                }
                Rectangle {                    // botón entrar
                    anchors.right: parent.right; anchors.rightMargin: 6
                    anchors.verticalCenter: parent.verticalCenter
                    width: 36; height: 36; radius: 18
                    color: goArea.containsMouse ? "#cdc6ff" : root.cAccent
                    Text {
                        anchors.centerIn: parent; anchors.horizontalCenterOffset: 1
                        text: "→"; color: "#241d4f"; font.pixelSize: 18; font.family: root.fUi
                    }
                    MouseArea { id: goArea; anchors.fill: parent; hoverEnabled: true; onClicked: root.doLogin() }
                }
            }

            Text {
                id: message
                Layout.fillWidth: true
                text: keyboard.capsLock ? "Bloq Mayús está activado" : ""
                color: "#ff9fb0"; font.family: root.fUi; font.pixelSize: 13
            }
        }

        SequentialAnimation {
            id: shake
            PropertyAnimation { target: card; property: "x"; to: card.x - 12; duration: 60; easing.type: Easing.OutQuad }
            PropertyAnimation { target: card; property: "x"; to: card.x + 10; duration: 80; easing.type: Easing.InOutQuad }
            PropertyAnimation { target: card; property: "x"; to: card.x - 6; duration: 70; easing.type: Easing.InOutQuad }
            PropertyAnimation { target: card; property: "x"; to: Math.round(root.width * 0.07); duration: 80; easing.type: Easing.OutQuad }
        }
    }

    function doLogin() {
        message.text = "Entrando…"
        sddm.login(userList.currentItem ? userList.currentItem.login : "", password.text, root.sessionIndex)
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            password.text = ""
            message.text = "Contraseña incorrecta"
            shake.start()
            password.forceActiveFocus()
        }
    }

    // ---- barra inferior: sesión y energía ------------------------------------------------
    RowLayout {
        anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.leftMargin: Math.round(root.width * 0.07); anchors.rightMargin: 40; anchors.bottomMargin: 34
        spacing: 10

        Pill {                                  // sesión (clic = siguiente)
            label: sessionList.currentItem ? sessionList.currentItem.sname : "Plasma"
            glyph: "◐"
            onClicked: root.sessionIndex = (root.sessionIndex + 1) % Math.max(1, sessionModel.rowCount())
        }
        ListView {
            id: sessionList
            Layout.preferredWidth: 1; Layout.preferredHeight: 1; opacity: 0
            model: sessionModel; currentIndex: root.sessionIndex
            delegate: Item { required property string name; property string sname: name }
        }
        Pill { visible: keyboard.layouts.length > 1; label: keyboard.layouts[keyboard.currentLayout] ? keyboard.layouts[keyboard.currentLayout].shortName.toUpperCase() : ""; glyph: "⌨"
               onClicked: keyboard.currentLayout = (keyboard.currentLayout + 1) % keyboard.layouts.length }
        Item { Layout.fillWidth: true }
        Pill { visible: sddm.canSuspend; label: "Reposo"; glyph: "☾"; onClicked: sddm.suspend() }
        Pill { visible: sddm.canReboot; label: "Reiniciar"; glyph: "↻"; onClicked: sddm.reboot() }
        Pill { visible: sddm.canPowerOff; label: "Apagar"; glyph: "⏻"; accent: true; onClicked: sddm.powerOff() }
    }

    component Pill: Rectangle {
        id: pill
        property string label
        property string glyph
        property bool accent: false
        signal clicked()
        implicitHeight: 38; implicitWidth: row.implicitWidth + 30
        radius: 19
        color: accent ? (pa.containsMouse ? "#40a69afe" : "#26a69afe") : (pa.containsMouse ? "#24ffffff" : "#14ffffff")
        border.color: accent ? root.cAccent : "#1fffffff"
        Row {
            id: row
            anchors.centerIn: parent
            spacing: 8
            Text { text: pill.glyph; color: pill.accent ? root.cAccent : root.cText; font.pixelSize: 15; anchors.verticalCenter: parent.verticalCenter }
            Text { text: pill.label; color: root.cText; font.family: root.fUi; font.pixelSize: 14; anchors.verticalCenter: parent.verticalCenter }
        }
        MouseArea { id: pa; anchors.fill: parent; hoverEnabled: true; onClicked: pill.clicked() }
    }

    Component.onCompleted: password.forceActiveFocus()
}
