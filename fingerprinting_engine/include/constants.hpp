//Global Constants. Sizing gauranteed by ffmpeg processing.

constexpr int WINDOW_SIZE = 4096;      // FFT window size in samples
constexpr int HOP_SIZE    = 2048;      // 50% overlap between windows
constexpr int SAMPLE_RATE = 44100;     // Expected input sample rate
constexpr int FAN_OUT     = 15;        // Max peak pairs per anchor point
constexpr int TARGET_TIME_WINDOW = 200; // Max time delta for peak pairing (in frames)
constexpr double MAGNITUDE_THRESHOLD = 1e-3; // Minimum peak magnitude
