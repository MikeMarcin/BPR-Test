#include "button.h"

void Button::click()
{
	if (Enabled && Handler) {
		Handler();
	}
}
