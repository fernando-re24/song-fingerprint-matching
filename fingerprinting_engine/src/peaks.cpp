#include "peaks.hpp"

constexpr double MAGNITUDE_THRESHOLD = 1e-3;

// Logarithmic frequency bands (bin index boundaries)
// At 44100 Hz / 4096 window ≈ 10.77 Hz per bin
static const std::vector<std::pair<int, int>> BANDS = {
    {0,   10},   // ~0-107 Hz    (sub-bass)
    {10,  20},   // ~107-215 Hz  (bass)
    {20,  40},   // ~215-430 Hz  (low-mid)
    {40,  80},   // ~430-861 Hz  (mid)
    {80,  160},  // ~861-1723 Hz (upper-mid)
    {160, 512},  // ~1723-5512 Hz (presence/brilliance)
};

std::vector<std::pair<int, int>> find_peaks(
    const std::vector<std::vector<double>>& spectrogram)
{
    std::vector<std::pair<int, int>> peaks;

    for (int t = 0; t < static_cast<int>(spectrogram.size()); t++) {
        const auto& frame = spectrogram[t];

        for (const auto& [band_start, band_end] : BANDS) {
            int best_bin = -1;
            double best_mag = MAGNITUDE_THRESHOLD;

            for (int f = band_start; f < band_end && f < static_cast<int>(frame.size()); f++) {
                if (frame[f] > best_mag) {
                    best_mag = frame[f];
                    best_bin = f;
                }
            }

            if (best_bin >= 0) {
                peaks.push_back({t, best_bin});
            }
        }
    }

    return peaks;
}
