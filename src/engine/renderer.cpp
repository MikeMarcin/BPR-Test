#include "renderer.h"

void Renderer::draw()
{
	clear();
	draw_scene();
	present();
}

void Renderer::resize(const int aWidth, const int aHeight)
{
	Width  = aWidth;
	Height = aHeight;
}
