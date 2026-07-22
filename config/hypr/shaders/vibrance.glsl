precision mediump float;
varying vec2 v_texcoord;
uniform sampler2D tex;

void main() {
    vec4 color = texture2D(tex, v_texcoord);
    float luma = dot(color.rgb, vec3(0.2126, 0.7152, 0.0722));
    vec3 satColor = mix(vec3(luma), color.rgb, 1.35);
    gl_FragColor = vec4(satColor, color.a);
}
