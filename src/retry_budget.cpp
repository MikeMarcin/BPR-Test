#include <algorithm>
#include <chrono>

// How long the next retry waits: doubles from 100 ms, capped at 5 s.
// The shift is bounded so a large attempt count cannot overflow.
std::chrono::milliseconds retry_delay(int attempt)
{
	const auto doublings = std::clamp(attempt, 0, 6);
	const auto delay     = std::chrono::milliseconds{ 100 } * (1 << doublings);
	return std::min(delay, std::chrono::milliseconds{ 5000 });
}
