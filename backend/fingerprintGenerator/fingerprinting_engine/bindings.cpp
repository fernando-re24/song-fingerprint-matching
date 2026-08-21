#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "fft.hpp"
#include "spectrogram.hpp"
#include "peaks.hpp"
#include "hash.hpp"
#include "fingerprint.hpp"

namespace py = pybind11;

PYBIND11_MODULE(fingerprint_engine, m) {
    m.doc() = "C++ audio fingerprinting engine";

    m.def("compute_fft", &compute_fft,
          "Compute FFT magnitude spectrum of an audio window",
          py::arg("signal"));

    m.def("generate_spectrogram", &generate_spectrogram,
          "Generate a time-frequency spectrogram from audio samples",
          py::arg("audio"));

    m.def("find_peaks", &find_peaks,
          "Find constellation peaks in a spectrogram",
          py::arg("spectrogram"));

    m.def("generate_hashes", &generate_hashes,
          "Generate combinatorial hashes from peak pairs",
          py::arg("peaks"));

    m.def("fingerprint_audio", &fingerprint_audio,
          "Full pipeline: audio samples -> fingerprint hashes",
          py::arg("audio"));
}
