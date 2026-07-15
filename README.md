# song-fingerprint-matching

An app that takes audio input and attempts to match input audio to known songs, based on the Shazam app.

## Design Choices

Python backend/orchestration calls a C++ processing library which does the heavy lifting in terms of
audio processing and key generation, after normalization of input with ffmpeg.

**C++ pipeline:**
Audio Buffer -> Windowing of Signal -> FFT -> Spectrogram -> Peak Detection -> Hash Generation
In: raw audio. Out: unique hashes. pybind11 provides the Python bindings.

**Matching:** offset-histogram voting. For each query hash, every known (song, offset) sharing that hash
casts a vote for `db_offset - query_offset`. A true match spikes in a single bin because the recording
lines up at a constant time delta; false matches scatter. Score is the tallest bin.

## Deployed Architecture (AWS)

```
Users -> Frontend
  |-- metadata ------> API Gateway ------> fingerprintGenerator (Lambda)
  |-- audio bytes ---> audio-payloads (S3, presigned URL) --^
                                                            |
                                                           SQS
                                                            |
                                                   matching-container (ECS/Fargate)
                                                            |
                                          songs-db (DynamoDB) + popular-songs (Redis)
                                                            |
                                          match payload -> API Gateway -> Frontend
```

- **audio-payloads (S3)** — raw uploads, written directly by the client via presigned URL.
- **fingerprintGenerator (Lambda)** — fingerprints the audio, enqueues the result.
- **SQS** — decouples fingerprinting from matching and absorbs bursts.
- **matching-container (ECS/Fargate)** — long-lived SQS consumer; this repo's `Dockerfile`.
- **songs-db (DynamoDB)** — single-table store for songs + fingerprints.
- **popular-songs (Redis/ElastiCache)** — *not yet implemented.* Will cache hash lookups, since popular
  songs dominate queries. `Matcher._postings_for_hash` is the single seam it slots into.

DynamoDB replaced the original MongoDB choice: the access pattern is a single-key hash lookup at high
volume, which is exactly what a DynamoDB GSI serves well, and it removes a self-managed database from
the deployment.

### songs-db single-table layout

| Item        | PK                 | SK                     | GSI `HashIndex` |
|-------------|--------------------|------------------------|-----------------|
| Song        | `SONG#<song_id>`   | `METADATA`             | —               |
| Fingerprint | `SONG#<song_id>`   | `FP#<hash>#<offset>`   | `hashIndex`     |

Co-locating a song's fingerprints under one partition key keeps per-song writes/deletes in a single
partition, while the GSI serves the hash -> songs lookup the matcher needs.

## matching-container

Build (targets `linux/amd64` for Fargate):

```bash
docker build -t matching-container .
```

Run locally:

```bash
docker run --rm \
  -e AWS_REGION=us-east-1 \
  -e MATCH_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/<acct>/<queue> \
  -e SONGS_TABLE_NAME=songs-db \
  -e AUDIO_BUCKET=audio-payloads \
  matching-container
```

Push to ECR:

```bash
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin <acct>.dkr.ecr.us-east-1.amazonaws.com
docker tag matching-container <acct>.dkr.ecr.us-east-1.amazonaws.com/matching-container:latest
docker push <acct>.dkr.ecr.us-east-1.amazonaws.com/matching-container:latest
```

### Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `AWS_REGION` | `us-east-1` | Region for all AWS clients |
| `MATCH_QUEUE_URL` | *(required)* | SQS queue to consume |
| `SONGS_TABLE_NAME` | `songs-db` | DynamoDB table |
| `AUDIO_BUCKET` | `audio-payloads` | S3 bucket for raw audio |
| `VISIBILITY_TIMEOUT` | `60` | SQS visibility timeout per receive |
| `LOG_LEVEL` | `INFO` | Log verbosity |

The worker handles `SIGTERM` so Fargate scale-in drains the in-flight message instead of dropping it,
and only deletes a message after a successful match, so failures are redelivered rather than lost.

## Ingestion

```bash
python -m scripts.ingest /path/to/songs
```

Normalizes each file, fingerprints it via the C++ engine, and writes song + fingerprint items to
DynamoDB. Expects filenames shaped `Artist - Title.ext`.

## Libraries

**Python:** boto3, pybind11, fastapi/uvicorn (API layer)
**C++:** FFTW3, pybind11
