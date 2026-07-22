#version 300 es
precision mediump float;
in vec2 v_texcoord;
out vec4 fragColor;
uniform sampler2D tex;

void main() {
    vec4 pixColor = texture(tex, v_texcoord);
    pixColor.g *= 0.85;
    pixColor.b *= 0.60;
    fragColor = pixColor;
}
