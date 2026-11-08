/* AxolOS · presentación durante la instalación (generada por tools/instalador_marca_axolos.py) */
import QtQuick 2.15
import calamares.slideshow 1.0

Presentation {
    id: presentation
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
            source: "diapositiva1.jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva2.jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva3.jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva4.jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
    Slide {
        anchors.fill: parent
        Image {
            anchors.fill: parent
            source: "diapositiva5.jpg"
            fillMode: Image.PreserveAspectCrop
            smooth: true; mipmap: true
        }
    }
}
