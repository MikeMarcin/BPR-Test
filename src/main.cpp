#include "engine/renderer.h"

int main()
{
	Renderer renderer;
	renderer.resize(1280, 720);
	renderer.draw();
	return 0;
}
