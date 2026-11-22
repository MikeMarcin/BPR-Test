#version 330 core
uniform sampler2D uScene;
in vec2 vUv;
out vec4 fragColour;
void main() { vec4 c = texture(uScene, vUv); fragColour = c / (c + vec4(1.0)); }
