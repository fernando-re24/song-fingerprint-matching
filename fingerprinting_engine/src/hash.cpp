#include "hash.hpp"

constexpr int FAN_OUT = 15;
constexpr int TARGET_TIME_WINDOW = 200;

std::vector<std::tuple<long, int>> generate_hashes(
    const std::vector<std::pair<int, int>>& peaks)
{
    std::vector<std::tuple<long, int>> hashes;

    for (size_t i = 0; i < peaks.size(); i++) {
        int anchor_time = peaks[i].first;
        int anchor_freq = peaks[i].second;
        int paired = 0;

        for (size_t j = i + 1; j < peaks.size() && paired < FAN_OUT; j++) {
            int target_time = peaks[j].first;
            int target_freq = peaks[j].second;
            int delta_time = target_time - anchor_time;

            // Skip peaks in the same time frame
            if (delta_time < 1) continue;
            // Stop once we've passed the target zone
            if (delta_time > TARGET_TIME_WINDOW) break;

            // Pack (anchor_freq, target_freq, delta_time) into 30 bits
            long hash = (static_cast<long>(anchor_freq & 0x3FF) << 20)
                      | (static_cast<long>(target_freq & 0x3FF) << 10)
                      | (static_cast<long>(delta_time & 0x3FF));

            hashes.push_back({hash, anchor_time});
            paired++;
        }
    }

    return hashes;
}
