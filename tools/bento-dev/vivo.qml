// Prueba del menú Bento con los modelos REALES de Plasma (favoritas, recientes,
// búsqueda, categorías). Saca 3 capturas: inicio, búsqueda y categoría.
import QtQuick
import QtQuick.Window
import org.kde.plasma.private.kicker as Kicker
import org.kde.coreaddons as KCoreAddons
import "../../packages/axolos-menu/org.axolos.bento/contents/ui"

Window {
    id: win
    width: 900; height: 520; visible: true; color: "#141418"
    readonly property string outDir: Qt.application.arguments[Qt.application.arguments.length - 1]
    Image { anchors.fill: parent; source: "file:///usr/share/wallpapers/AxolOS/contents/images/2730x1536.jpg"; fillMode: Image.PreserveAspectCrop; opacity: 0.35 }

    Kicker.RootModel {
        id: rootModel
        autoPopulate: false; flat: true; sorted: true; showSeparators: false
        showTopLevelItems: true; showAllApps: true; showAllAppsCategorized: false
        showRecentApps: false; showRecentDocs: false; showPowerSession: false; showFavoritesPlaceholder: false
        Component.onCompleted: { favoritesModel.initForClient("org.kde.plasma.kickoff.favorites.instance-262"); refresh() }
    }
    Kicker.RecentUsageModel { id: recentModel; shownItems: Kicker.RecentUsageModel.OnlyDocs }
    Kicker.RunnerModel { id: runnerModel; mergeResults: true; favoritesModel: rootModel.favoritesModel }
    Kicker.SystemModel { id: systemModel }
    KCoreAddons.KUser { id: kuser }

    BentoView {
        id: view
        anchors.centerIn: parent
        width: implicitWidth; height: implicitHeight
        userName: kuser.fullName || kuser.loginName
        faceIcon: kuser.faceIconUrl
        favoritesModel: rootModel.favoritesModel
        recentModel: recentModel
        resultsModel: runnerModel.count > 0 ? runnerModel.modelForRow(0) : null
        rootModel: rootModel
        systemModel: systemModel
        appCount: rootModel.count > 0 ? rootModel.modelForRow(0).count : 0
        battery: 100; networkText: "StarlinkMarchena"
        onQueryChanged: runnerModel.query = query
    }
    property int step: 0
    Timer {
        id: t; interval: 2500; running: true
        onTriggered: win.contentItem.grabToImage(function (r) {
            r.saveToFile(win.outDir + "/vivo-" + win.step + ".png")
            win.step++
            if (win.step === 1) { view.setQuery("konso"); t.interval = 2500; t.restart() }
            else if (win.step === 2) { view.setQuery(""); view.category = 3; t.interval = 1500; t.restart() }
            else Qt.quit()
        })
    }
    Component.onCompleted: console.log("filas", rootModel.count, "favoritas", rootModel.favoritesModel.count, "recientes", recentModel.count, "sistema", systemModel.count)
}
