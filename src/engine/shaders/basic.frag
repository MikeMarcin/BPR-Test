#version 330 core
in vec4 vColour;
uniform float uExposure;
out vec4 fragColour;
void main() { fragColour = vColour * uExposure; }
