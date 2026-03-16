#ifndef FINGERPRINT_HPP
#define FINGERPRINT_HPP

#include <vector>
#include <tuple>

std::vector<std::tuple<long,int>> fingerprint_audio(
    const std::vector<double>& audio
);

#endif
