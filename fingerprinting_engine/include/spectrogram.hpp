#ifndef SPECTROGRAM_HPP
#define SPECTROGRAM_HPP

#include <vector>

std::vector<std::vector<double>> generate_spectrogram(
    const std::vector<double>& audio
);

#endif
