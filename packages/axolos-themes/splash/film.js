.pragma library
// AxolOS · película de arranque. ÚNICA fuente de tiempos.
// Todo son funciones puras de t (segundos): cualquier fotograma se puede
// dibujar en cualquier orden.
//
// Duración pensada para el arranque REAL medido en este equipo: KSplash está
// en pantalla ~2,1 s (journal: plasma-ksplash.service, 2.140s). La película
// cuenta su historia en 1,9 s y termina siendo el escritorio; si el arranque
// tarda más, el ajolote espera vivo y aparece la marca.

var T = {
    ant0: 0.00,     // se echa atrás mientras sube su luz
    walk0: 0.12,    // empieza a caminar
    step: 0.22,     // un paso (un par diagonal de patas)
    walk1: 1.12,    // ~4,5 pasos después llega (y se pasa un poco)
    settle: 1.50,   // asentado
    flick0: 1.15,   // coletazo
    eye: 1.33,      // destello en el ojo
    iris0: 1.38,    // iris de luz desde el ojo
    iris1: 1.82,    // mundo encendido = escritorio
    swap1: 1.94,    // relevo invisible al fondo exacto de Plasma (0,12 s)
    end: 1.95,      // fin de la historia; después, espera en bucle
    hud0: 2.80      // la marca solo aparece si el arranque es lento
};
var TRAVEL = 470;       // px del fondo que recorre caminando
var OVERSHOOT = 24;     // se pasa al frenar
var LEAN = 12;          // anticipación hacia atrás

// Puntos del ajolote en px del fondo (rejilla del logo → px: x·189,2+296, y·148,4+72)
function U(x, y) { return [296 + x * 189.2, 72 + y * 148.4]; }
var EYE = U(2.95, 6.10);
var CENTER = U(5.0, 5.0);
// Patas: pivote (= rig) y apoyo del pie en reposo. "off" = desfase del ciclo:
// pares diagonales (del.-izq. + tras.-der.) y (del.-der. + tras.-izq.)
var LEGS = {
    legFL: { pivot: [570.3, 1029.2], foot: U(0.75, 7.30), off: 0.0, max: 58 },
    legBR: { pivot: [1733.9, 443.0], foot: U(7.60, 5.40), off: 0.0, max: 40 },
    legFR: { pivot: [1270.4, 969.8], foot: U(4.60, 8.60), off: 0.5, max: 40 },
    legBL: { pivot: [1535.3, 539.5], foot: U(6.10, 4.60), off: 0.5, max: 44 }
};
var STANCE = 0.62;      // fracción del ciclo con el pie apoyado

function clamp(x, a, b) { return Math.max(a, Math.min(b, x)); }
function lin(t, a, b) { return clamp((t - a) / (b - a), 0, 1); }
function smooth(x) { return x * x * (3 - 2 * x); }
function easeInOutSine(x) { return -(Math.cos(Math.PI * x) - 1) / 2; }
function easeOutCubic(x) { return 1 - Math.pow(1 - x, 3); }
function easeInOutCubic(x) { return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; }
function bump(t, a, m, b) {
    if (t <= a || t >= b) return 0;
    return t < m ? smooth((t - a) / (m - a)) : smooth((b - t) / (b - m));
}

// Perfil de avance con velocidad trapezoidal (acelera, crucero, frena)
function trap(w, r) {
    if (w <= 0) return 0;
    if (w >= 1) return 1;
    var k = 1 / (1 - r);
    if (w < r) return k * w * w / (2 * r);
    if (w > 1 - r) return 1 - k * (1 - w) * (1 - w) / (2 * r);
    return k * (w - r / 2);
}

// Posición horizontal del cuerpo (px del fondo, 0 = su sitio en el fondo)
function X(t) {
    if (t < T.walk0) return TRAVEL + LEAN * smooth(lin(t, T.ant0, T.walk0));
    if (t < T.walk1) {
        var w = lin(t, T.walk0, T.walk1);
        return (TRAVEL + LEAN) - (TRAVEL + LEAN + OVERSHOOT) * trap(w, 0.22);
    }
    var u = t - T.walk1;
    return -OVERSHOOT * Math.exp(-7 * u) * Math.cos(10 * u) * (1 - lin(t, T.settle - 0.1, T.settle + 0.15));
}
function V(t) { return (X(t + 0.005) - X(t - 0.005)) / 0.01; }   // px/s

// Ángulo de una pata para que el pie no resbale mientras apoya.
// Girar θ (horario) el vector pie f=(fx,fy): fx·cosθ − fy·sinθ = G − pivoteX
function plantedAngle(L, g) {
    var fx = L.foot[0] - L.pivot[0], fy = L.foot[1] - L.pivot[1];
    var R = Math.hypot(fx, fy), phi = Math.atan2(fy, fx);
    return (Math.acos(clamp(g / R, -1, 1)) - phi) * 180 / Math.PI;
}
function legAngle(L, t) {
    if (t <= T.walk0 - 2 * T.step) return 0;
    var P = 2 * T.step;
    var u = (t - T.walk0) / P + L.off;
    var k = Math.floor(u), c = u - k;
    var fx = L.foot[0] - L.pivot[0];
    function ts(n) { return T.walk0 + (n - L.off) * P; }
    var R = Math.hypot(fx, L.foot[1] - L.pivot[1]);
    // El pie se apoya donde estaría en reposo con el cuerpo a mitad de la
    // zancada; si la pata no llega tan lejos, apoya un poco más atrás (alcance).
    function stanceAt(n, tt) {
        var a = ts(n), b = a + STANCE * P;
        var mid = (X(a) + X(b)) / 2, half = Math.abs(X(a) - X(b)) / 2;
        var lim = Math.max(0, 0.78 * R - half);   // zona cómoda de la articulación
        var center = clamp(fx, -lim, lim);
        return plantedAngle(L, center + mid - X(tt));
    }
    var th;
    if (c < STANCE) th = stanceAt(k, t);
    else {
        var from = stanceAt(k, ts(k) + STANCE * P), to = stanceAt(k + 1, ts(k + 1));
        th = from + (to - from) * easeInOutSine((c - STANCE) / (1 - STANCE));
    }
    th = clamp(th, -L.max, L.max);
    return th * (1 - smooth(lin(t, T.settle - 0.05, T.settle + 0.30)));   // exacto en 0 al terminar el iris
}

// ---------------------------------------------------------------- personaje
function pose(t, exitP) {
    var p = { legFL: 0, legFR: 0, legBL: 0, legBR: 0, tail: 0, bodyRot: 0, bodyX: 0, bodyY: 0 };
    p.bodyX = X(t);
    for (var n in LEGS) p[n] = legAngle(LEGS[n], t);

    var env = smooth(lin(t, T.walk0, T.walk0 + 0.10)) * (1 - smooth(lin(t, T.walk1 - 0.10, T.walk1 + 0.05)));
    var ph = Math.max(0, t - T.walk0) / T.step;
    var s = Math.sin(Math.PI * ph);
    p.bodyY = -6 * Math.abs(s) * env;                         // sube en cada paso
    p.bodyRot = 0.8 * s * env + 1.2 * bump(t, T.ant0, 0.08, T.walk0 + 0.06);
    p.tail = clamp(0.0024 * V(t), -2.6, 2.6);                 // inercia: la cola se queda atrás

    var brake = bump(t, T.walk1 - 0.12, T.walk1 + 0.02, T.walk1 + 0.25);
    p.bodyRot += -0.9 * brake;

    var k = lin(t, T.flick0, T.flick0 + 0.40);                // coletazo amortiguado
    if (k > 0 && k < 1) p.tail += 3.2 * Math.sin(2 * Math.PI * k) * (1 - k);

    // Espera (arranque lento): el cuerpo queda en su pose exacta; la vida la da el ojo
    return p;
}

// ---------------------------------------------------------------- cámara y luz
function world(t, p) {
    return {
        scale: 0.965 + 0.035 * easeOutCubic(lin(t, 0, T.settle)),   // empuje de cámara
        camX: 0,
        parallax: 0,
        key: smooth(lin(t, 0.0, 0.22)),                            // su luz se enciende
        lightI: 1.1 * smooth(lin(t, 0.0, 0.30)),
        glint: bump(t, T.eye - 0.05, T.eye + 0.04, T.eye + 0.30)
             + (t > T.end + 1.5 ? 0.55 * bump((t - T.end - 1.5) % 3.5, 0, 0.12, 0.5) : 0),
        iris: easeInOutCubic(lin(t, T.iris0, T.iris1)) * 2.1,
        desk: smooth(lin(t, T.iris1, T.swap1))
    };
}

// ---------------------------------------------------------------- interfaz
function hud(t, exitP) {
    var open = easeOutCubic(lin(t, T.hud0, T.hud0 + 0.45)) * (1 - easeInOutCubic(exitP));
    var typed = Math.floor(Math.max(0, t - (T.hud0 + 0.25)) * 28);
    return { open: open, typed: typed };
}

function events() {
    return [
        { t: T.ant0, name: "anticipación" }, { t: T.walk0, name: "primer paso" },
        { t: T.walk1, name: "frenada" }, { t: T.flick0, name: "coletazo" },
        { t: T.eye, name: "abre el ojo" }, { t: T.iris0, name: "iris de luz" },
        { t: T.iris1, name: "escritorio" }, { t: T.hud0, name: "marca (arranque lento)" }
    ];
}
