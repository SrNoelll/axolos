// AxolOS · cristal líquido real (refracción, dispersión y brillo) para QtQuick.
// Compilar: tools/shaders_cristal.sh (qsb). El fondo que se ve detrás llega como dos texturas
// (nítida y desenfocada) de TODA la escena; «zona» es el rectángulo de este elemento dentro de ella.
#version 440
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;
layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    vec2 tam;           // tamaño del elemento (px)
    vec4 zona;          // x, y, ancho, alto del elemento dentro de la escena (0..1)
    float radio;        // radio de las esquinas (px)
    float bisel;        // ancho del borde curvo que hace de lente (px)
    float fuerza;       // cuánto desplaza la lente el fondo (px)
    float dispersion;   // separación de colores en el borde (arcoíris)
    vec4 tinte;         // color del cristal (alfa = cuánto tiñe)
    float brillo;       // intensidad de brillos y filo
};
layout(binding = 1) uniform sampler2D nitido;
layout(binding = 2) uniform sampler2D borroso;

float caja(vec2 p, vec2 b, float r) {
    vec2 q = abs(p) - b + r;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

vec3 fondo(vec2 uv, float nitidez) {
    return mix(texture(borroso, uv).rgb, texture(nitido, uv).rgb, nitidez);
}

void main() {
    vec2 b = tam * 0.5;
    vec2 p = (qt_TexCoord0 - 0.5) * tam;
    float d = caja(p, b, radio);                       // < 0 dentro
    float alfa = clamp(0.5 - d, 0.0, 1.0);             // borde suavizado
    if (alfa <= 0.0) { fragColor = vec4(0.0); return; }

    // normal del borde (gradiente de la distancia) y perfil de la lente
    vec2 n = vec2(caja(p + vec2(1.0, 0.0), b, radio) - caja(p - vec2(1.0, 0.0), b, radio),
                  caja(p + vec2(0.0, 1.0), b, radio) - caja(p - vec2(0.0, 1.0), b, radio));
    n /= max(length(n), 1e-4);
    float t = clamp(1.0 + d / bisel, 0.0, 1.0);        // 0 en el interior, 1 en el borde
    float curva = pow(t, 2.6);
    float suave = t * t * (3.0 - 2.0 * t);

    // refracción: el borde curvo mira hacia dentro; cada color se desvía distinto (dispersión)
    vec2 uv = zona.xy + qt_TexCoord0 * zona.zw;
    vec2 desp = -n * curva * fuerza * (zona.zw / tam);
    float nitidez = suave * 0.65;                      // el vidrio grueso del borde deja ver más nítido
    vec3 c;
    c.r = fondo(uv + desp * (1.0 + dispersion), nitidez).r;
    c.g = fondo(uv + desp, nitidez).g;
    c.b = fondo(uv + desp * (1.0 - dispersion), nitidez).b;
    c = mix(c, tinte.rgb, tinte.a);

    // brillos: luz desde arriba a la izquierda, reflejo frío abajo y un filo fino en el contorno
    vec2 luz = normalize(vec2(-0.55, -0.85));
    float spec = pow(max(dot(n, luz), 0.0), 2.0) * curva;
    float spec2 = pow(max(dot(n, -luz), 0.0), 3.0) * curva;
    float filo = 1.0 - smoothstep(0.0, 1.6, -d);
    c += brillo * (vec3(1.0) * spec * 0.42 + vec3(0.75, 0.80, 1.0) * spec2 * 0.14 + vec3(1.0) * filo * 0.20);
    fragColor = vec4(c, 1.0) * alfa * qt_Opacity;
}
