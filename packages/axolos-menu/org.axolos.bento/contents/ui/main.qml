/*
    AxolOS · Bento — menú de aplicaciones (plasmoide).
    Usa los mismos modelos que el menú de KDE: comparte tus favoritas, lee tus
    recientes, busca con KRunner y apaga/reinicia con las acciones del sistema.
    SPDX-License-Identifier: GPL-3.0-or-later
*/
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import org.kde.plasma.private.kicker as Kicker
import org.kde.plasma.plasma5support as P5Support
import org.kde.plasma.networkmanagement as PlasmaNM
import org.kde.coreaddons as KCoreAddons

PlasmoidItem {
    id: root

    Plasmoid.icon: Plasmoid.configuration.icon || "axolos"
    toolTipMainText: i18n("Applications")
    toolTipSubText: i18n("Favorites, recent files and search")
    // en el panel: botón; suelto (escritorio o ventana): el menú completo
    preferredRepresentation: Plasmoid.formFactor === PlasmaCore.Types.Planar ? fullRepresentation : compactRepresentation
    hideOnWindowDeactivate: true

    // «Wi-Fi: Conectado a Casa» → «Casa», en cualquier idioma: plasma-nm escribe «dispositivo: estado»
    // y la plantilla del estado sale de su propio catálogo («Connecté à %1», «%1 に接続済み»…)
    readonly property var plantillaRed: i18nd("plasmanetworkmanagement-libs", "Connected to %1", "\u0001").split("\u0001")
    function nombreRed(linea) {
        const antes = plantillaRed[0], despues = plantillaRed.length > 1 ? plantillaRed[1] : ""
        const sep = linea.indexOf(": ")
        const estado = sep >= 0 ? linea.slice(sep + 2) : linea
        const conectado = (!antes.length || estado.startsWith(antes)) && (!despues.length || estado.endsWith(despues))
        if (!conectado) return linea                       // conectando, sin internet…: tal cual
        return estado.slice(antes.length, despues.length ? -despues.length : undefined)
    }

    // ---- modelos de Plasma -----------------------------------------------------
    Kicker.RootModel {
        id: kRoot
        autoPopulate: false
        appletInterface: root
        flat: true
        sorted: true
        showSeparators: false
        showTopLevelItems: true
        showAllApps: true
        showAllAppsCategorized: false
        showRecentApps: false
        showRecentDocs: false
        showPowerSession: false
        showFavoritesPlaceholder: false
        Component.onCompleted: {
            favoritesModel.initForClient("org.kde.plasma.kickoff.favorites.instance-" + Plasmoid.id)
            if (!Plasmoid.configuration.favoritesPortedToKAstats) {
                if (favoritesModel.count < 1)
                    favoritesModel.portOldFavorites(Plasmoid.configuration.favorites)
                Plasmoid.configuration.favoritesPortedToKAstats = true
            }
            // Primera vez: completa las favoritas con lo que trae todo AxolOS
            if (!Plasmoid.configuration.favoritesSeeded) {
                const extra = ["preferred://filemanager", "preferred://browser",
                               "applications:org.kde.konsole.desktop", "applications:org.axolos.ia.desktop",
                               "applications:org.axolos.centro.desktop", "applications:systemsettings.desktop"]
                for (const id of extra) {
                    if (favoritesModel.count >= 8) break
                    if (!favoritesModel.isFavorite(id)) favoritesModel.addFavorite(id, -1)
                }
                Plasmoid.configuration.favoritesSeeded = true
            }
        }
    }
    Kicker.RecentUsageModel {
        id: kRecent
        shownItems: Kicker.RecentUsageModel.OnlyDocs
        ordering: Kicker.RecentUsageModel.Recent
    }
    Kicker.RunnerModel {
        id: kRunner
        appletInterface: root
        mergeResults: true
        favoritesModel: kRoot.favoritesModel
    }
    Kicker.SystemModel { id: kSystem }

    P5Support.DataSource {
        id: pm
        engine: "powermanagement"
        connectedSources: ["Battery"]
    }
    PlasmaNM.NetworkStatus { id: net }
    KCoreAddons.KUser { id: kuser }

    readonly property var allApps: kRoot.count > 0 ? kRoot.modelForRow(0) : null

    onExpandedChanged: (expanded) => { if (expanded) kRoot.refresh() }

    // ---- botón del dock ---------------------------------------------------------
    compactRepresentation: MouseArea {
        id: button
        hoverEnabled: true
        onClicked: root.expanded = !root.expanded
        // cuadrado del alto del dock (como los iconos de la barra de tareas)
        readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
        Layout.minimumWidth: vertical ? -1 : height
        Layout.preferredWidth: vertical ? -1 : height
        Layout.minimumHeight: vertical ? width : -1
        Layout.preferredHeight: vertical ? width : -1
        Kirigami.Icon {
            anchors.fill: parent
            anchors.margins: 0
            source: Plasmoid.icon
            active: button.containsMouse || root.expanded
        }
    }

    // ---- el menú -----------------------------------------------------------------
    fullRepresentation: Item {
        Layout.preferredWidth: view.implicitWidth
        Layout.preferredHeight: view.implicitHeight
        Layout.minimumWidth: view.implicitWidth
        Layout.minimumHeight: view.implicitHeight

        BentoView {
            id: view
            anchors.fill: parent
            framed: false                       // el popup ya pone el fondo (con desenfoque)
            focus: true
            userName: kuser.fullName || kuser.loginName
            faceIcon: kuser.faceIconUrl
            favoritesModel: kRoot.favoritesModel
            recentModel: kRecent
            resultsModel: kRunner.count > 0 ? kRunner.modelForRow(0) : null
            rootModel: kRoot
            systemModel: kSystem
            appCount: root.allApps ? root.allApps.count : 0
            battery: pm.data["Battery"] && pm.data["Battery"]["Has Battery"] ? pm.data["Battery"]["Percent"] : -1
            networkText: root.nombreRed(net.activeConnections.split("\n")[0])

            onQueryChanged: kRunner.query = query
            onLaunch: (model, row) => {
                model.trigger(row, "", null)
                root.expanded = false
            }
            onCloseRequested: root.expanded = false

            Timer {
                interval: 15000; repeat: true; running: root.expanded
                onTriggered: view.now = new Date()
            }
            Connections {                       // al abrir: hora al día, búsqueda vacía y foco
                target: root
                function onExpandedChanged() {
                    if (root.expanded) { view.now = new Date(); view.reset() }
                }
            }
        }
    }
}
