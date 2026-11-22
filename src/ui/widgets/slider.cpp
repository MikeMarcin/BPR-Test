#include "slider.h"

void Slider::set_value(const int aValue)
{
	Value = aValue < Minimum ? Minimum : (aValue > Maximum ? Maximum : aValue);
}
