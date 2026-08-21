#ifndef HASH_HPP
#define HASH_HPP

#include <vector>
#include <tuple>
#include <utility>

// Generate combinatorial hashes from peak pairs.
// Input: sorted list of peaks as (time_frame, frequency_bin)
// Output: list of (hash_value, anchor_time_offset)
std::vector<std::tuple<long, int>> generate_hashes(
    const std::vector<std::pair<int, int>>& peaks
);

#endif
