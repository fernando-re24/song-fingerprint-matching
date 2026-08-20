#include "spectrogram.hpp"
#include "fft.hpp"

constexpr int WINDOW_SIZE = 4096;
constexpr int HOP_SIZE = 2048;

std::vector<std::vector<double>> generate_spectrogram(const std::vector<double>& audio) {
    std::vector<std::vector<double>> spectrogram;

    if (audio.size() < static_cast<size_t>(WINDOW_SIZE)) {
        return spectrogram;
    }

    int num_frames = static_cast<int>((audio.size() - WINDOW_SIZE) / HOP_SIZE) + 1;
    spectrogram.reserve(num_frames);

    for (int frame = 0; frame < num_frames; frame++) {
        int start = frame * HOP_SIZE;
        std::vector<double> window(audio.begin() + start,
                                   audio.begin() + start + WINDOW_SIZE);
        spectrogram.push_back(compute_fft(window));
    }

    return spectrogram;
}
