#include <charconv>
#include <optional>
#include <string_view>

// Reads a TCP port from text such as "8080".
// Accepts 1..65535 and nothing else: no sign, no spaces, no trailing text.
std::optional<unsigned> parse_port(std::string_view text)
{
	if (text.empty() || text.size() > 5) {
		return std::nullopt;
	}
	unsigned value = 0;
	const auto [end, error] = std::from_chars(text.data(), text.data() + text.size(), value);
	if (error != std::errc{} || end != text.data() + text.size()) {
		return std::nullopt;
	}
	if (value == 0 || value > 65535) {
		return std::nullopt;
	}
	return value;
}
