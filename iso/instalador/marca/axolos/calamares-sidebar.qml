/* AxolOS · barra de pasos del instalador (abajo), con los colores de la marca */
import io.calamares.ui 1.0
import io.calamares.core 1.0
import QtQuick 2.3
import QtQuick.Layouts 1.3

Rectangle {
    id: sideBar
    color: Branding.styleString(Branding.SidebarBackground)
    height: 46
    width: parent ? parent.width : 0      // al crearse aún no tiene padre
    Rectangle { anchors.top: parent.top; width: parent.width; height: 1; color: "#2a2a34" }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 12; anchors.rightMargin: 12
        spacing: 4
        Image {
            Layout.alignment: Qt.AlignVCenter
            Layout.rightMargin: 8
            width: 28; height: 28
            sourceSize.width: 28; sourceSize.height: 28
            source: "file:/" + Branding.imagePath(Branding.ProductLogo)
        }
        Repeater {
            model: ViewManager
            Rectangle {
                readonly property bool actual: index == ViewManager.currentStepIndex
                readonly property bool hecho: index < ViewManager.currentStepIndex
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignVCenter
                height: 30
                radius: 15
                color: actual ? Branding.styleString(Branding.SidebarBackgroundCurrent) : "transparent"
                Text {
                    anchors.centerIn: parent
                    width: parent.width - 8
                    horizontalAlignment: Text.AlignHCenter
                    elide: Text.ElideRight
                    text: display
                    color: parent.actual ? Branding.styleString(Branding.SidebarTextCurrent)
                         : (parent.hecho ? "#e6e6ee" : Branding.styleString(Branding.SidebarText))
                    font.weight: parent.actual ? Font.DemiBold : Font.Normal
                    font.pointSize: 9.5
                }
            }
        }
    }
}
