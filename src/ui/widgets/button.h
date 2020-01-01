#pragma once

#include <functional>

class Button
{
public:
	void click();

	std::function<void()> Handler;
	bool                  Enabled = true;
};
