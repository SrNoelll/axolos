/*
    AxolOS · pantalla de inicio de sesión (SDDM, Qt 6)
    Tu fondo, un reloj grande, y una tarjeta de cristal con el avatar del
    ajolote y la contraseña. Paleta y tipografías de AxolOS.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import QtQuick.Effects
import SddmComponents 2.0          // TextConstants: textos de SDDM traducidos al idioma del sistema

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
    function two(n) { return (n < 10 ? "0" : "") + n }

    // ---- idioma y formato regional del sistema -----------------------------------
    TextConstants { id: textConstants }
    readonly property var loc: Qt.locale()
    readonly property bool reloj12: loc.timeFormat(Locale.ShortFormat).toLowerCase().indexOf("ap") >= 0
    // formato largo de la región sin el año («domingo, 8 de noviembre», «Sunday, November 8»…)
    readonly property string formatoFecha: loc.dateFormat(Locale.LongFormat)
        .replace(/y+\s*[年년]\s*/, "")
        .replace(/^y+[.,]?\s*/, "")
        .replace(/\s*'[^']*'\s*y+/, "")
        .replace(/[,.]?\s*y+(\s*'[^']*'\.?)?/, "")
        .trim()
    function hora(d) {
        return reloj12 ? (d.getHours() % 12 || 12) + ":" + two(d.getMinutes()) + " " + d.toLocaleTimeString(loc, "AP")
                       : two(d.getHours()) + ":" + two(d.getMinutes())
    }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }

    // ---- fondo (la escena que refracta el cristal) -----------------------------------
    Item {
        id: escenaFondo
        anchors.fill: parent
        Image {
            id: bg
            anchors.fill: parent
            source: config.background || "/usr/share/wallpapers/AxolOS/contents/images_dark/3840x2160.jpg"
            fillMode: Image.PreserveAspectCrop
            asynchronous: false
        }
        Rectangle {                       // velo para que el texto se lea siempre
            anchors.fill: parent
            gradient: Gradient {
                orientation: Gradient.Horizontal
                GradientStop { position: 0.0; color: "#a0050506" }
                GradientStop { position: 0.55; color: "#30050506" }
                GradientStop { position: 1.0; color: "#08050506" }
            }
        }
    }
    // la misma escena desenfocada (solo se usa como textura del cristal)
    MultiEffect {
        id: escenaBorrosa
        anchors.fill: parent
        source: escenaFondo
        autoPaddingEnabled: false
        blurEnabled: true; blur: 1.0; blurMax: 48
        saturation: 0.15
    }
    // texturas compartidas por todos los cristales de la pantalla
    readonly property var texNitido: ShaderEffectSource { sourceItem: escenaFondo }
    readonly property var texBorroso: ShaderEffectSource { sourceItem: escenaBorrosa; hideSource: true }

    // ---- reloj ---------------------------------------------------------------------
    Column {
        x: Math.round(root.width * 0.07); y: Math.round(root.height * 0.12)
        spacing: 4
        Text {
            text: root.hora(root.now)
            color: root.cText; font.family: root.fDisplay; font.pixelSize: Math.round(root.height * 0.13)
        }
        Text {
            leftPadding: 6
            text: root.now.toLocaleDateString(root.loc, root.formatoFecha || "dddd d MMMM")
            color: root.cMuted; font.family: root.fUi; font.pixelSize: Math.round(root.height * 0.024)
        }
    }

    // ---- tarjeta de acceso ---------------------------------------------------------
    Item {
        id: card
        width: 400; height: 214
        x: Math.round(root.width * 0.07); y: Math.round(root.height * 0.52)

        // cristal líquido real: refracta y separa en colores el fondo de detrás
        Cristal {
            anchors.fill: parent
            escena: escenaFondo; nitido: root.texNitido; borroso: root.texBorroso
            radio: 26; bisel: 30; fuerza: 46; dispersion: 0.34
            tinte: Qt.rgba(0.07, 0.07, 0.09, 0.32)
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
                        text: textConstants.password
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
                text: keyboard.capsLock ? textConstants.capslockWarning : ""
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
            message.text = textConstants.loginFailed
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
        Pill { visible: sddm.canSuspend; label: textConstants.suspend; glyph: "☾"; onClicked: sddm.suspend() }
        Pill { visible: sddm.canReboot; label: textConstants.reboot; glyph: "↻"; onClicked: sddm.reboot() }
        Pill { visible: sddm.canPowerOff; label: textConstants.shutdown; glyph: "⏻"; accent: true; onClicked: sddm.powerOff() }
    }

    component Pill: Rectangle {
        id: pill
        property string label
        property string glyph
        property bool accent: false
        signal clicked()
        implicitHeight: 38; implicitWidth: row.implicitWidth + 30
        radius: 19
        color: "transparent"
        border.color: accent ? root.cAccent : "transparent"
        Cristal {
            anchors.fill: parent
            z: -1
            escena: escenaFondo; nitido: root.texNitido; borroso: root.texBorroso
            radio: 19; bisel: 16; fuerza: 18; dispersion: 0.36
            tinte: pill.accent ? Qt.rgba(0.65, 0.6, 1.0, pa.containsMouse ? 0.32 : 0.22)
                               : Qt.rgba(0.07, 0.07, 0.09, pa.containsMouse ? 0.18 : 0.30)
        }
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
