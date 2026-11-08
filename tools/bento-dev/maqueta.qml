// Maqueta a tamaño real del menú Bento sobre tu escritorio (datos reales).
// Uso: tools/bento-dev/render.sh <salida.png>
import QtQuick
import QtQuick.Window
import QtQuick.Effects
import org.kde.kirigami as Kirigami
import "../../packages/axolos-menu/org.axolos.bento/contents/ui"

Window {
    id: win
    width: 1920; height: 1080; visible: true; color: "black"
    readonly property string out: Qt.application.arguments[Qt.application.arguments.length - 1]

    Item {
        id: desk
        anchors.fill: parent
        Image {
            id: wall
            anchors.fill: parent
            source: "file:///usr/share/wallpapers/AxolOS/contents/images/2730x1536.jpg"
            fillMode: Image.PreserveAspectCrop
            sourceSize: Qt.size(1920, 1080)
        }

        // Desenfoque de fondo detrás del menú (lo que hará KWin con el efecto blur)
        Item {
            id: blurClip
            x: menu.x; y: menu.y; width: menu.width; height: menu.height
            clip: true
            MultiEffect {
                x: -blurClip.x; y: -blurClip.y
                width: desk.width; height: desk.height
                source: wall
                blurEnabled: true; blur: 1.0; blurMax: 64
                saturation: -0.2
            }
            layer.enabled: true
            layer.effect: MultiEffect {
                maskEnabled: true
                maskSource: ShaderEffectSource {
                    sourceItem: Rectangle { width: menu.width; height: menu.height; radius: 26 }
                }
            }
        }

        BentoView {
            id: menu
            width: implicitWidth; height: implicitHeight
            x: (parent.width - width) / 2
            y: dock.y - height - 14
            userName: "Noel"
            appCount: 123
            wifiName: "StarlinkMarchena"
            battery: 100
            focusedFavorite: 0
            categories: ["Internet", "Desarrollo", "Multimedia", "Juegos", "Oficina"]
            favorites: [
                { name: "Dolphin", icon: "org.kde.dolphin" },
                { name: "Brave", icon: "brave-desktop" },
                { name: "Konsole", icon: "utilities-terminal" },
                { name: "Preferencias", icon: "preferences-system" },
                { name: "Antigravity", icon: "antigravity" },
                { name: "Claude", icon: "claude-desktop" },
                { name: "Discord", icon: "discord" },
                { name: "Heroic", icon: "com.heroicgameslauncher.hgl" }
            ]
            recents: [
                { name: "CLAUDE_1.md", icon: "text-markdown", where: "Descargas" },
                { name: "control_wifi.sh", icon: "text-x-script", where: "Auditoria_WiFi" },
                { name: "fondoAjo.jpg", icon: "image-jpeg", where: "Imágenes" }
            ]
        }

        // Dock (como el tuyo)
        Rectangle {
            id: dock
            readonly property var icons: ["axolos", "system-file-manager", "brave-desktop", "antigravity",
                                          "utilities-terminal", "preferences-system", "claude-desktop"]
            width: row.implicitWidth + 24; height: 70
            x: (parent.width - width) / 2; y: parent.height - height - 8
            radius: 18
            color: "#d9141418"; border.color: "#16ffffff"
            Row {
                id: row
                anchors.centerIn: parent
                spacing: 14
                Repeater {
                    model: dock.icons
                    delegate: Kirigami.Icon {
                        required property string modelData
                        required property int index
                        width: 52; height: 52
                        source: modelData
                        Rectangle {                  // el botón del menú, activo
                            visible: index === 0
                            anchors.fill: parent; anchors.margins: -5
                            radius: 14; color: "#1fa69afe"; border.color: "#a69afe"; z: -1
                        }
                    }
                }
            }
        }
    }

    Timer {
        interval: 2500; running: true
        onTriggered: desk.grabToImage(function (r) { r.saveToFile(win.out); Qt.quit() })
    }
}
