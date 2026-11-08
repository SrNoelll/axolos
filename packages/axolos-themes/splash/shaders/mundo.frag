#version 440
// AxolOS · el mundo: oscuro salvo la luz que lleva el ajolote; luego un iris
// de luz sale de su ojo y lo enciende todo (al final = el fondo tal cual).
layout(location = 0) in vec2 qt_TexCoord0;
layout(location = 0) out vec4 fragColor;

layout(std140, binding = 0) uniform buf {
    mat4 qt_Matrix;
    float qt_Opacity;
    float lightX;   // luz del ajolote (0..1 en la placa)
    float lightY;
    float lightI;
    float eyeX;     // centro del iris = su ojo (0..1)
    float eyeY;
    float iris;     // radio del iris (en alturas de la placa)
    float aspect;   // ancho / alto de la placa
};
layout(binding = 1) uniform sampler2D source;   // placa (fondo sin patas)
layout(binding = 2) uniform sampler2D hole;     // dónde está el ajolote del fondo

void main() {
    vec2 uv = qt_TexCoord0;
    vec3 c = texture(source, uv).rgb;
    float h = texture(hole, uv).r;

    vec2 dl = (uv - vec2(lightX, lightY)) * vec2(aspect, 1.0);
    float pool = lightI * exp(-dot(dl, dl) / 0.30);          // charco de luz
    float dark = (0.045 + pool) * (1.0 - smoothstep(0.0, 0.55, h));   // sombra suave, sin silueta

    vec2 de = (uv - vec2(eyeX, eyeY)) * vec2(aspect, 1.0);
    float d = length(de);
    float soft = 0.16;
    float lit = 1.0 - smoothstep(iris - soft, iris, d);      // dentro del iris: luz plena
    float rim = smoothstep(iris - soft, iris - soft * 0.5, d) * (1.0 - smoothstep(iris - soft * 0.5, iris, d));

    vec3 col = c * mix(dark, 1.0, lit) + c * rim * 0.35 * step(0.001, iris);
    fragColor = vec4(col, 1.0) * qt_Opacity;
}
