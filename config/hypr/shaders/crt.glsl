precision mediump float;
varying vec2 v_texcoord;
uniform sampler2D tex;

void main() {
    vec4 color = texture2D(tex, v_texcoord);
    float scanline = sin(v_texcoord.y * 800.0) * 0.04;
    color.rgb -= scanline;
    gl_FragColor = color;
}
