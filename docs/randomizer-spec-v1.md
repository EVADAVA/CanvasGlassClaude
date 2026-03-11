# CanvasGlassNew Randomizer Spec v1

## Purpose

`Randomizer` assembles one episode as a unique signature before render.

It operates between content loading and FFmpeg orchestration.

## Pipeline

`content loader -> randomizer -> episode manifest -> ffmpeg orchestrator -> final render`

## Base Inputs

- three painting backgrounds
- rendered monologues `MON1..MON4`
- real monologue durations after trim
- `QRE` cue inside `MON1`
- `QRp1..QRp3` target links
- episode seed

## Signature Model

`episode_signature = audio_signature + video_signature + timing_signature`

## Audio Signature

- ambience stays very low under speech
- ambience rises only slightly in silence
- voice remains dominant at all times
- track choice, offsets, and levels are rolled from seed

## Video Signature

Finalized live-image modules for the test render:

- `micro_zoom_drift`
- `subtle_pan_drift`
- `lens_breath`
- `exposure_breathing`
- `passing_shadow`

These modules should make the frame feel alive, not damaged.

## Timing Signature

- `QRE` appears at the actual playlist cue inside `MON1`
- `QRp1..QRp3` appear at `segment_end - 60s`
- video events avoid obvious overlap with QR windows
- spacing stays irregular enough to avoid a mechanical rhythm

## Current Test Render Shape

- total runtime: `15:00`
- painting 1: `0:00-5:00`
- painting 2: `5:00-10:00`
- painting 3: `10:00-15:00`
- `MON1` starts at `0:00`
- `MON2` starts at `5:00`
- `MON3` starts at `10:00`
- `MON4` starts at `13:00`

## Test Render Output

The current test renderer writes:

- manifest: `/Users/akg/EVADAVA/CanvasGlassNew/output/generated/test15_signature_manifest.json`
- filter graph: `/Users/akg/EVADAVA/CanvasGlassNew/output/generated/test15_signature_filter.txt`
- video: `/Users/akg/EVADAVA/CanvasGlassNew/output/video_render_test15_signature.mp4`
