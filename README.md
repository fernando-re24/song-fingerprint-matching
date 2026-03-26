# song-fingerprint-matching
An app that takes audio input and attempts to match input audio to known songs, based on the shazam app.

## Design Choices:
  Python backend/orchestration calls c++ processing library which does the heavy lifting in terms of audio processing and key generation after normalization of input with ffmpeg
  C++ Pipeline Design
  Audio Buffer -> Windowing of Signal -> FFT -> Spectrogram -> Peak Detection -> Hash Generation
  In: Raw audio. Out: Unique Hash
  Will add fuzz factor after basic implementation
  Use of pybind11 for c++ bindings 
  Once the we have the hash, the backend will send the hash through the matching algorithm
  Nearest neighbors matching
  Mongo was chosen because we don’t need a strict schema and are dealing with a large dataset that needs simple key lookups w/ hash as the index.
  Trial with personal collection of files initially, then move on to worrying about sourcing
  FastApi will be used for async, speed, easy handling of uploads
  Docker-compose to link the fastapi, mongodb, and c++ processing containers.
  Distributed Matching For the larger database implementation.
  Redis to cache frequent lookups (popular songs).
  Could be implemented on specific pods s.t. Different regions with different tastes can have their popular requests cached.
  Kubernetes will be set up to facilitate mock-distributed system

## Schemas:

  songs
  {
    _id: ObjectId,
    title: "Song Name",
    artist: "Artist",
    duration: 210
  }
  
  fingerprints:
  {
    hash: 123456789,
    song_id: ObjectId,
    time_offset: 52.1
  }



## Libraries:

  Python:
  Ffmpeg python
  fastapi
  uvicorn
  pydub
  numpy
  motor (async MongoDB)
  pybind11
  
  C++:
  FFTW
  Eigen
  pybind11
