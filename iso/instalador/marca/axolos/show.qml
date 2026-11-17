/* AxolOS · presentación durante la instalación (generada por tools/instalador_marca_axolos.py) */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
    // Idioma de las diapositivas: lo traduce lang/calamares-axolos_<idioma>.qm según el idioma elegido
    // en el instalador (es, fr, ru, zh_CN, ja); con cualquier otro, inglés.
    readonly property string idioma: qsTr("en", "slides language code")
    Rectangle { anchors.fill: parent; color: "#0f0f13"; z: -1 }
    Timer {
        interval: 12000
        running: presentation.activatedInCalamares
        repeat: true
        onTriggered: presentation.goToNextSlide()
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva1." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva2." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva3." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva4." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva5." + presentation.idioma + ".jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
}
