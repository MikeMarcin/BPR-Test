#include <chrono>

// How long the next retry waits: doubles from 100 ms, capped at 5 s.
std::chrono::milliseconds retry_delay(int attempt)
{
	auto delay = std::chrono::milliseconds{ 100 };
	for (int i = 0; i < attempt; ++i) {
		delay *= 2;
	}
	return delay > std::chrono::seconds{ 5 } ? std::chrono::milliseconds{ 5000 } : delay;
}
