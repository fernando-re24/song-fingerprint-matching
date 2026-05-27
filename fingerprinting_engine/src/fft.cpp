#include "fft.hpp"
#include <fftw3.h>
#include <cmath>

std::vector<double> compute_fft(const std::vector<double>& signal) {
    int N = static_cast<int>(signal.size());
    int out_size = N / 2 + 1;

    double* in = fftw_alloc_real(N);
    fftw_complex* out = fftw_alloc_complex(out_size);

    // Apply Hanning window to reduce spectral leakage
    for (int i = 0; i < N; i++) {
        double window = 0.5 * (1.0 - cos(2.0 * M_PI * i / (N - 1)));
        in[i] = signal[i] * window;
    }

    // Real-to-complex FFT: only N/2+1 complex bins needed (output is symmetric)
    fftw_plan plan = fftw_plan_dft_r2c_1d(N, in, out, FFTW_ESTIMATE);
    fftw_execute(plan);

    // Convert complex FFT output to magnitude spectrum
    std::vector<double> magnitudes(out_size);
    for (int i = 0; i < out_size; i++) {
        double re = out[i][0];
        double im = out[i][1];
        magnitudes[i] = sqrt(re * re + im * im);
    }

    fftw_destroy_plan(plan);
    fftw_free(in);
    fftw_free(out);

    return magnitudes;
}
