// AxolOS · reloj del escritorio arriba a la derecha, sea cual sea la resolución de la pantalla.
// Plasma guarda la posición de los widgets en píxeles por resolución: copiada de un equipo, en una
// pantalla distinta no cabe y Plasma lo manda arriba a la izquierda. Por eso no va en /etc/skel:
// se crea aquí, una sola vez por usuario, medido sobre su pantalla. Si ya hay reloj, no se toca.
var TAM = 272;
desktops().forEach(function (d) {
    if (d.screen !== 0 || d.widgets("org.kde.plasma.analogclock").length > 0)
        return;
    var g = screenGeometry(d.screen);
    d.addWidget("org.kde.plasma.analogclock", Math.max(0, g.width - TAM), 0, TAM, TAM);
});
