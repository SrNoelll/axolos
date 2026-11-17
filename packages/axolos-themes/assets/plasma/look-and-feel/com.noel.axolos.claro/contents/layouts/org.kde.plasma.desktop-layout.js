// AxolOS · disposición del escritorio (generado por tools/diseno_axolos.py desde skel; no editar a mano)
// Plasma borra paneles y widgets y ejecuta esto al aplicar el tema con «Diseño del escritorio».

desktops().forEach(function (d) {
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "/usr/share/wallpapers/AxolOS/");
});

var panel234 = new Panel;
panel234.location = "top";
panel234.height = 40;
panel234.floating = true;
panel234.opacity = "translucent";
var w238 = panel234.addWidget("org.kde.plasma.appmenu");
var w239 = panel234.addWidget("org.kde.plasma.panelspacer");
var w240 = panel234.addWidget("org.kde.plasma.marginsseparator");
var w241 = panel234.addWidget("org.kde.plasma.systemtray");
var w254 = panel234.addWidget("org.kde.plasma.marginsseparator");
var w255 = panel234.addWidget("org.kde.plasma.digitalclock");
var w256 = panel234.addWidget("org.kde.plasma.showdesktop");
var w265 = panel234.addWidget("org.kde.plasma.keyboardlayout");

var panel236 = new Panel;
panel236.location = "bottom";
panel236.height = 70;
panel236.lengthMode = "fit";
panel236.hiding = "dodgewindows";
panel236.floating = true;
panel236.opacity = "translucent";
var w270 = panel236.addWidget("org.axolos.bento");
var w237 = panel236.addWidget("org.kde.plasma.icontasks");
w237.currentConfigGroup = ["General"];
w237.writeConfig("launchers", ["preferred://filemanager", "preferred://browser", "applications:org.axolos.ia.desktop", "applications:org.kde.konsole.desktop", "applications:systemsettings.desktop"]);

// reloj del escritorio
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
