#include "button.h"

void Button::click()
{
	if (Handler) {
		Handler();
	}
}
