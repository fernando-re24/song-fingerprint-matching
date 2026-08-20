#include "fingerprint.hpp"
#include "spectrogram.hpp"
#include "peaks.hpp"
#include "hash.hpp"

std::vector<std::tuple<long, int>> fingerprint_audio(const std::vector<double>& audio) {
    // Step 1: Generate time-frequency representation
    auto spec = generate_spectrogram(audio);

    // Step 2: Extract constellation peaks
    auto peak_points = find_peaks(spec);

    // Step 3: Generate combinatorial hashes from peak pairs
    auto hashes = generate_hashes(peak_points);

    return hashes;
}
