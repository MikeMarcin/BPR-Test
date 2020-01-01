#version 330 core
uniform sampler2D uScene;
in vec2 vUv;
out vec4 fragColour;
void main() { fragColour = texture(uScene, vUv) * 1.2; }
