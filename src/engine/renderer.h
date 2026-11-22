#pragma once

class Renderer
{
public:
	void draw();
	void resize(int aWidth, int aHeight);

private:
	void clear();
	void draw_scene();
	void present();

	int Width  = 0;
	int Height = 0;
};
