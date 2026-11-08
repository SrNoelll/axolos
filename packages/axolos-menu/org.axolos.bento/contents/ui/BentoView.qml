/*
    AxolOS · Bento — la vista del menú.
    Recibe los modelos de Plasma (favoritas, recientes, búsqueda, categorías,
    sistema) y emite qué abrir. Vistas: inicio (mosaicos), categoría y búsqueda.
    Teclado: escribir busca · flechas mueven · Intro abre · Esc vuelve/cierra.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as QQC2
import QtQuick.Effects
import org.kde.kirigami as Kirigami

FocusScope {
    id: bento

    // ---- datos ----------------------------------------------------------------
    property string userName: ""          // lo pone main.qml (nombre completo o de la cuenta)
    property url faceIcon
    property var now: new Date()
    property var favoritesModel: null
    property var recentModel: null
    property var resultsModel: null        // resultados de búsqueda (fusionados)
    property var rootModel: null           // fila 0 = todas, resto = categorías
    property var systemModel: null
    property string networkText: ""
    property int battery: -1
    property int appCount: 0
    property bool framed: true             // dibuja su propio panel (maqueta) o no (dentro del popup)

    readonly property string query: search.text
    property int category: -1              // -1 = inicio · ≥0 = fila de rootModel
    readonly property var categoryModel: (rootModel && category >= 0) ? rootModel.modelForRow(category) : null
    readonly property string view: query.length ? "search" : (category >= 0 ? "category" : "home")

    signal launch(var model, int row)
    signal closeRequested()

    // ---- estilo AxolOS ---------------------------------------------------------
    readonly property color cPanel: "#e6141418"
    readonly property color cTile: "#0fffffff"
    readonly property color cHover: "#1aa69afe"
    readonly property color cLine: "#16ffffff"
    readonly property color cText: "#ececf1"
    readonly property color cMuted: "#9b9ba8"
    readonly property color cAccent: "#a69afe"
    readonly property string fDisplay: "New York Extra Large"
    readonly property string fUi: "SF Pro Display"
    readonly property string fMono: "iA Writer Mono S"
    readonly property real tileH: 118

    implicitWidth: 796
    implicitHeight: column.implicitHeight + 44

    function reset() { search.text = ""; category = -1; search.forceActiveFocus() }
    function setQuery(t) { search.text = t }
    function greeting(d) {
        const h = d.getHours()
        return h < 6 ? "Buenas noches" : h < 13 ? "Buenos días" : h < 21 ? "Buenas tardes" : "Buenas noches"
    }
    function two(n) { return (n < 10 ? "0" : "") + n }
    readonly property var dias: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
    readonly property var meses: ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                  "septiembre", "octubre", "noviembre", "diciembre"]

    Keys.onEscapePressed: {
        if (search.text.length) search.text = ""
        else if (category >= 0) category = -1
        else closeRequested()
    }

    Rectangle {
        anchors.fill: parent
        visible: bento.framed
        radius: 26
        color: bento.cPanel
        border.color: bento.cLine
    }

    ColumnLayout {
        id: column
        anchors.fill: parent
        anchors.margins: 22
        spacing: 16

        // ---- cabecera: avatar, saludo y búsqueda ------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: 14
            Rectangle {
                Layout.preferredWidth: 46; Layout.preferredHeight: 46
                radius: 23; color: "#1d1b2a"; border.color: bento.cAccent; border.width: 1.5
                Item {                                   // foto recortada en círculo de verdad
                    anchors.fill: parent; anchors.margins: 2.5
                    Image {
                        id: face
                        anchors.fill: parent
                        source: bento.faceIcon
                        fillMode: Image.PreserveAspectCrop
                        visible: false
                        layer.enabled: true
                    }
                    Rectangle { id: faceMask; anchors.fill: parent; radius: width / 2; visible: false; layer.enabled: true }
                    MultiEffect {
                        anchors.fill: parent
                        source: face
                        maskEnabled: true; maskSource: faceMask
                        maskThresholdMin: 0.5; maskSpreadAtMin: 1.0
                        visible: face.status === Image.Ready
                    }
                }
                Kirigami.Icon {
                    anchors.centerIn: parent; width: 30; height: 30
                    visible: face.status !== Image.Ready
                    source: "axolos"; fallback: "start-here-kde"
                }
            }
            ColumnLayout {
                spacing: 0
                Text {
                    text: bento.greeting(bento.now) + (bento.userName.length ? ", " + bento.userName.charAt(0).toUpperCase() + bento.userName.slice(1) : "")
                    color: bento.cText; font.family: bento.fDisplay; font.pixelSize: 25
                }
                Text {
                    text: bento.appCount + " aplicaciones"
                    color: bento.cMuted; font.family: bento.fMono; font.pixelSize: 12
                }
            }
            Item { Layout.fillWidth: true }
            Rectangle {
                Layout.preferredWidth: 330; Layout.preferredHeight: 42
                radius: 14
                color: "#0affffff"
                border.color: search.activeFocus || search.text.length ? bento.cAccent : bento.cLine
                border.width: search.text.length ? 1.5 : 1
                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 14; anchors.rightMargin: 10
                    spacing: 10
                    Kirigami.Icon { Layout.preferredWidth: 18; Layout.preferredHeight: 18; source: "search"; isMask: true; color: bento.cMuted }
                    TextInput {
                        id: search
                        Layout.fillWidth: true
                        focus: true
                        color: bento.cText
                        selectionColor: "#7662ce"
                        font.family: bento.fUi; font.pixelSize: 14
                        clip: true
                        Text {
                            anchors.fill: parent; verticalAlignment: Text.AlignVCenter
                            visible: !search.text.length
                            text: "Busca apps, archivos o ajustes"
                            color: bento.cMuted; font: search.font
                        }
                        Keys.onDownPressed: results.forceActiveFocus()
                        Keys.onReturnPressed: if (bento.view === "search" && bento.resultsModel && bento.resultsModel.count > 0) bento.launch(bento.resultsModel, results.currentIndex)
                        Keys.onEnterPressed: Keys.onReturnPressed(event)
                        onTextChanged: results.currentIndex = 0
                    }
                }
            }
        }

        // ---- cuerpo -----------------------------------------------------------
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: bento.tileH * 2 + 12

            // Inicio: mosaicos
            GridLayout {
                anchors.fill: parent
                visible: bento.view === "home"
                columns: 4; rowSpacing: 12; columnSpacing: 12

                Tile {
                    Layout.columnSpan: 2; Layout.rowSpan: 2
                    Layout.fillWidth: true; Layout.preferredWidth: 2
                    Layout.preferredHeight: bento.tileH * 2 + 12
                    title: "Favoritas"
                    GridView {
                        id: favGrid
                        anchors.fill: parent; anchors.topMargin: 24
                        interactive: false
                        cellWidth: Math.floor(width / 4); cellHeight: Math.floor(height / 2)
                        model: bento.favoritesModel
                        delegate: AppCell {
                            width: favGrid.cellWidth; height: favGrid.cellHeight
                            onClicked: bento.launch(bento.favoritesModel, index)
                        }
                    }
                }
                Tile {                                   // reloj
                    Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: bento.tileH
                    Text {
                        anchors.left: parent.left; anchors.top: parent.top
                        text: "AHORA"; color: bento.cAccent
                        font.family: bento.fMono; font.pixelSize: 11; font.letterSpacing: 2
                    }
                    Text {
                        anchors.left: parent.left; anchors.bottom: dateTxt.top; anchors.bottomMargin: -4
                        text: bento.two(bento.now.getHours()) + ":" + bento.two(bento.now.getMinutes())
                        color: bento.cText; font.family: bento.fDisplay; font.pixelSize: 42
                    }
                    Text {
                        id: dateTxt
                        anchors.left: parent.left; anchors.bottom: parent.bottom
                        text: bento.dias[bento.now.getDay()] + " " + bento.now.getDate() + " de " + bento.meses[bento.now.getMonth()]
                        color: bento.cMuted; font.family: bento.fUi; font.pixelSize: 13
                    }
                }
                Tile {                                   // sistema
                    Layout.fillWidth: true; Layout.preferredWidth: 1; Layout.preferredHeight: bento.tileH
                    title: "Sistema"
                    ColumnLayout {
                        anchors.left: parent.left; anchors.right: parent.right; anchors.bottom: parent.bottom
                        spacing: 9
                        StatusRow { icon: "network-wireless-symbolic"; label: bento.networkText || "Sin conexión" }
                        StatusRow {
                            visible: bento.battery >= 0
                            icon: "battery-full-symbolic"; label: "Batería"; value: bento.battery + " %"
                            bar: bento.battery / 100
                        }
                    }
                }
                Tile {                                   // seguir con
                    Layout.columnSpan: 2
                    Layout.fillWidth: true; Layout.preferredWidth: 2; Layout.preferredHeight: bento.tileH
                    title: "Seguir con"
                    ListView {
                        id: recentList
                        anchors.fill: parent; anchors.topMargin: 24
                        interactive: false; clip: true
                        model: bento.recentModel
                        delegate: QQC2.ItemDelegate {
                            width: recentList.width; height: 26
                            visible: index < 3
                            background: Rectangle { radius: 8; color: parent.hovered ? bento.cHover : "transparent" }
                            contentItem: RowLayout {
                                spacing: 10
                                Kirigami.Icon { Layout.preferredWidth: 20; Layout.preferredHeight: 20; source: model.decoration }
                                Text { Layout.fillWidth: true; text: model.display; elide: Text.ElideMiddle; color: bento.cText; font.family: bento.fUi; font.pixelSize: 13 }
                                Text { text: (model.description || "").replace(/\/$/, "").split("/").pop(); elide: Text.ElideLeft; Layout.maximumWidth: 160; color: bento.cMuted; font.family: bento.fMono; font.pixelSize: 11 }
                            }
                            onClicked: bento.launch(bento.recentModel, index)
                        }
                    }
                    Text {
                        visible: !bento.recentModel || bento.recentModel.count === 0
                        anchors.centerIn: parent
                        text: "Aquí aparecerán tus archivos recientes"
                        color: bento.cMuted; font.family: bento.fUi; font.pixelSize: 13
                    }
                }
            }

            // Categoría: rejilla de apps
            Tile {
                anchors.fill: parent
                visible: bento.view === "category"
                title: bento.rootModel && bento.category >= 0 ? bento.rootModel.labelForRow(bento.category) : ""
                GridView {
                    id: catGrid
                    anchors.fill: parent; anchors.topMargin: 24
                    clip: true
                    cellWidth: Math.floor(width / 7); cellHeight: 104
                    model: bento.categoryModel
                    boundsBehavior: Flickable.StopAtBounds
                    delegate: AppCell {
                        width: catGrid.cellWidth; height: catGrid.cellHeight
                        onClicked: bento.launch(bento.categoryModel, index)
                    }
                    QQC2.ScrollBar.vertical: QQC2.ScrollBar {}
                }
            }

            // Búsqueda: lista de resultados
            Tile {
                anchors.fill: parent
                visible: bento.view === "search"
                ListView {
                    id: results
                    anchors.fill: parent
                    clip: true
                    model: bento.resultsModel
                    highlightMoveDuration: 0
                    keyNavigationEnabled: true
                    boundsBehavior: Flickable.StopAtBounds
                    delegate: QQC2.ItemDelegate {
                        width: results.width; height: 46
                        readonly property bool current: ListView.isCurrentItem
                        background: Rectangle {
                            radius: 12
                            color: parent.current ? "#22a69afe" : parent.hovered ? bento.cHover : "transparent"
                            border.color: parent.current ? bento.cAccent : "transparent"
                        }
                        contentItem: RowLayout {
                            spacing: 12
                            Kirigami.Icon { Layout.preferredWidth: 30; Layout.preferredHeight: 30; source: model.decoration }
                            ColumnLayout {
                                spacing: 0
                                Text { text: model.display; color: bento.cText; font.family: bento.fUi; font.pixelSize: 14; elide: Text.ElideRight; Layout.fillWidth: true }
                                Text { visible: text.length; text: model.description || ""; color: bento.cMuted; font.family: bento.fUi; font.pixelSize: 12; elide: Text.ElideRight; Layout.fillWidth: true }
                            }
                            Text { visible: parent.parent.current; text: "Intro"; color: bento.cMuted; font.family: bento.fMono; font.pixelSize: 11 }
                        }
                        onClicked: bento.launch(bento.resultsModel, index)
                    }
                    Keys.onReturnPressed: bento.launch(bento.resultsModel, currentIndex)
                    Keys.onEnterPressed: bento.launch(bento.resultsModel, currentIndex)
                    Keys.onUpPressed: currentIndex > 0 ? decrementCurrentIndex() : search.forceActiveFocus()
                    Keys.onPressed: (e) => { if (e.text.length && !e.modifiers) { search.forceActiveFocus(); search.text += e.text; e.accepted = true } }
                }
                Text {
                    visible: !bento.resultsModel || bento.resultsModel.count === 0
                    anchors.centerIn: parent
                    text: "Sin resultados para «" + bento.query + "»"
                    color: bento.cMuted; font.family: bento.fUi; font.pixelSize: 13
                }
            }
        }

        // ---- pie: categorías y energía ----------------------------------------
        RowLayout {
            Layout.fillWidth: true
            spacing: 10
            ListView {
                id: chips
                Layout.fillWidth: true; Layout.preferredHeight: 32
                orientation: ListView.Horizontal
                spacing: 6; clip: true
                boundsBehavior: Flickable.StopAtBounds
                model: bento.rootModel ? bento.rootModel.count + 1 : 1    // "Inicio" + filas
                delegate: Rectangle {
                    readonly property int row: index - 1
                    readonly property bool on: bento.category === row && !bento.query.length
                    readonly property bool empty: index > 0 && !chipTxt.text.length
                    visible: !empty
                    height: 32; width: empty ? -6 : chipTxt.implicitWidth + 26
                    radius: 16
                    color: on ? bento.cAccent : chipArea.containsMouse ? "#1affffff" : "#0dffffff"
                    Text {
                        id: chipTxt
                        anchors.centerIn: parent
                        text: index === 0 ? "Inicio" : (bento.rootModel ? bento.rootModel.labelForRow(row) : "")
                        color: parent.on ? "#1f1a3d" : bento.cText
                        font.family: bento.fUi; font.pixelSize: 13
                        font.weight: parent.on ? Font.Medium : Font.Normal
                    }
                    MouseArea {
                        id: chipArea
                        anchors.fill: parent; hoverEnabled: true
                        onClicked: { search.text = ""; bento.category = parent.row; search.forceActiveFocus() }
                    }
                }
            }
            Repeater {                                   // reposo · reiniciar · salir · apagar
                model: bento.systemModel
                delegate: Rectangle {
                    readonly property var wanted: ({ "suspend": 0, "reboot": 1, "logout": 2, "shutdown": 3 })
                    readonly property bool shown: model.favoriteId in wanted
                    readonly property bool danger: model.favoriteId === "shutdown"
                    visible: shown
                    Layout.preferredWidth: shown ? 36 : 0; Layout.preferredHeight: 36
                    radius: 18
                    color: danger ? (pArea.containsMouse ? "#40a69afe" : "#26a69afe") : (pArea.containsMouse ? "#1fffffff" : "#0dffffff")
                    border.color: danger ? bento.cAccent : "transparent"
                    Kirigami.Icon {
                        anchors.centerIn: parent; width: 18; height: 18
                        // Versión simbólica: con isMask, un icono a color (Yaru los tiene en PNG) sale como un cuadrado
                        source: ({ "suspend": "system-suspend-symbolic", "reboot": "system-reboot-symbolic",
                                   "logout": "system-log-out-symbolic", "shutdown": "system-shutdown-symbolic" })[model.favoriteId]
                                || model.decoration
                        isMask: true
                        color: parent.danger ? bento.cAccent : bento.cText
                    }
                    QQC2.ToolTip.visible: pArea.containsMouse
                    QQC2.ToolTip.text: model.display
                    MouseArea {
                        id: pArea
                        anchors.fill: parent; hoverEnabled: true
                        onClicked: bento.launch(bento.systemModel, index)
                    }
                }
            }
        }
    }

    // ---- piezas ----------------------------------------------------------------
    component Tile: Rectangle {
        property string title: ""
        default property alias content: inner.data
        radius: 18
        color: bento.cTile
        border.color: bento.cLine; border.width: 1
        Text {
            visible: parent.title.length > 0
            x: 16; y: 13
            text: parent.title
            color: bento.cMuted; font.family: bento.fUi; font.pixelSize: 13
        }
        Item { id: inner; anchors.fill: parent; anchors.margins: 14 }
    }

    component AppCell: Item {
        id: cell
        required property var model
        required property int index
        signal clicked()
        Rectangle {
            anchors.centerIn: parent
            width: Math.min(parent.width, parent.height) - 6; height: width
            radius: 16
            color: cellArea.containsMouse ? bento.cHover : "transparent"
            border.color: cellArea.containsMouse ? bento.cAccent : "transparent"
            border.width: 1.2
        }
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 6
            Kirigami.Icon {
                Layout.alignment: Qt.AlignHCenter
                implicitWidth: 48; implicitHeight: 48
                source: cell.model.decoration
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                Layout.maximumWidth: cell.width - 10
                text: cell.model.display
                elide: Text.ElideRight
                horizontalAlignment: Text.AlignHCenter
                color: bento.cText; font.family: bento.fUi; font.pixelSize: 12
            }
        }
        MouseArea {
            id: cellArea
            anchors.fill: parent; hoverEnabled: true
            onClicked: cell.clicked()
        }
    }

    component StatusRow: ColumnLayout {
        property string icon
        property string label
        property string value: ""
        property real bar: -1
        spacing: 6
        Layout.fillWidth: true
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Kirigami.Icon { Layout.preferredWidth: 16; Layout.preferredHeight: 16; source: icon; isMask: true; color: bento.cAccent }
            Text { Layout.fillWidth: true; text: label; elide: Text.ElideRight; color: bento.cText; font.family: bento.fUi; font.pixelSize: 13 }
            Text { text: value; color: bento.cMuted; font.family: bento.fMono; font.pixelSize: 12 }
        }
        Rectangle {
            visible: bar >= 0
            Layout.fillWidth: true; Layout.preferredHeight: 4
            radius: 2; color: "#14ffffff"
            Rectangle { width: parent.width * Math.max(0, bar); height: parent.height; radius: 2; color: bento.cAccent }
        }
    }
}
