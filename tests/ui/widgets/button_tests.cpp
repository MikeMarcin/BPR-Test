#include "ui/widgets/button.h"

int main()
{
	auto clicked = false;
	Button button;
	button.Handler = [&] { clicked = true; };
	button.Enabled = false;
	button.click();
	return clicked ? 1 : 0;
}
