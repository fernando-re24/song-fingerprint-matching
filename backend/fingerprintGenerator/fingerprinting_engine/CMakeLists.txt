cmake_minimum_required(VERSION 3.16)
project(fingerprint_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(FFTW3 REQUIRED fftw3)

find_package(pybind11 REQUIRED)

pybind11_add_module(fingerprint_engine
    src/fft.cpp
    src/spectrogram.cpp
    src/peaks.cpp
    src/hash.cpp
    src/fingerprint.cpp
    bindings.cpp
)

target_include_directories(fingerprint_engine PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
    ${FFTW3_INCLUDE_DIRS}
)

target_link_directories(fingerprint_engine PRIVATE
    ${FFTW3_LIBRARY_DIRS}
)

target_link_libraries(fingerprint_engine PRIVATE
    ${FFTW3_LIBRARIES}
)

install(TARGETS fingerprint_engine DESTINATION .)
