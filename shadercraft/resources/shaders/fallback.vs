#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;
layout (location = 2) in vec3 normal;

out vec3 pix_position;
out vec3 pix_color;
out vec3 pix_normal;

void main() {
	pix_position = position;
	pix_color = color;
	pix_normal = normal;

	gl_Position = vec4(pix_position, 1.0);
}
