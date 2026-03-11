# CanvasGlassNew Session Sync

Last updated: 2026-03-10

## Read This First

After restart, read this file first:

- [/Users/akg/EVADAVA/CanvasGlassNew/SESSION_SYNC.md](/Users/akg/EVADAVA/CanvasGlassNew/SESSION_SYNC.md)

Then, if needed:

- [/Users/akg/EVADAVA/CanvasGlassNew/docs/project-model.md](/Users/akg/EVADAVA/CanvasGlassNew/docs/project-model.md)

## Canonical Project Path

- `/Users/akg/EVADAVA/CanvasGlassNew`

## Current Video State

- Current 15-minute master:
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/video_render_test15_signature.mp4`
- Current render manifest:
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/generated/test15_signature_manifest.json`
- Current render script:
  - `/Users/akg/EVADAVA/CanvasGlassNew/scripts/render_test15_signature.py`
- Monologue renders:
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/renders/mon1_render.mp4`
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/renders/mon2_render.mp4`
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/renders/mon3_render.mp4`
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/renders/mon4_render.mp4`

## Current Composition Logic

- Backgrounds:
  - `test1.png` for 5:00
  - `test2.png` for 5:00
  - `test3.png` for 5:00
- Total duration:
  - `15:00`
- Monologue placement:
  - `MON1` starts at `0`
  - `MON2` starts at `300`
  - `MON3` starts at `600`
  - `MON4` starts at `780`
- First `4` seconds are trimmed from each avatar render before compositing.
- Avatar circle is bottom-left.
- Current avatar behavior in test render:
  - `MON1` plays as moving avatar
  - `MON2` is frozen avatar
  - `MON3` is frozen avatar
  - `MON4` is frozen avatar

## Current QR Rules

- `QRE` appears at the actual playlist cue inside `MON1`.
- `QRp1`, `QRp2`, `QRp3` appear at `segment_end - 60s`.
- All QR surfaces are in the `top-right` corner.
- Right-bottom corner must remain free for future channel watermark / copyright protection.
- User UX rule:
  - playlist QR and painting QR must train the viewer to look at the same information corner

## Current Signature Render Rules

- Randomized render is now treated as:
  - `audio_signature`
  - `video_signature`
  - `timing_signature`
- Current reference spec:
  - `/Users/akg/EVADAVA/CanvasGlassNew/docs/randomizer-spec-v1.md`
- Current test render video modules:
  - `micro_zoom_drift`
  - `subtle_pan_drift`
  - `lens_breath`
  - `passing_shadow`
- Current motion direction after user correction:
  - keep movement much less visible
  - scale should stay around `100-101%`, slow and smooth
  - position drift should stay around `1-2 px`
  - third painting must be especially stable because the white frame makes motion more visible
- Current event density direction:
  - defects should be farther apart
  - likely next rule: no major visible event closer than about `2 minutes`

## Known Open Issue

- The avatar badge still needs the final visual fix:
  - no white inner border
  - only a thin gold ring
  - look should match a gold seal
- Best visual reference currently:
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/diag/mon1_gold_ring_preview_zoom.png`

## Gold Ring Assets

- Old derived ring:
  - `/Users/akg/EVADAVA/CanvasGlassNew/logos/Profile_Double_ring.png`
- Better thin ring:
  - `/Users/akg/EVADAVA/CanvasGlassNew/logos/gold_ring_thin.png`

## Audio Assets

- Original gallery ambience WAVs:
  - `/Users/akg/EVADAVA/CanvasGlassNew/assets/audio/asmr_gallery`
- Compiled lossless FLAC copies:
  - `/Users/akg/EVADAVA/CanvasGlassNew/assets/audio/asmr_gallery/compiled_lossless`

These FLAC copies were created so the originals remain untouched.

## Agreed Audio Direction

- Gallery ambience is not foreground ASMR.
- It should sit very low under the voice as a near-subliminal gallery bed.
- Purpose:
  - preserve living-space feel
  - support the final video mix
- Voice remains dominant.
- User clarification:
  - noise floor should be even quieter than the first signature test
  - during speech it must be very low
  - during silence it can rise only slightly

## HeyGen / Monologue Notes

- `MON1..MON4` are generated and rendered.
- Template path works.
- Actual rendered monologue duration must be treated as a system parameter for final assembly.
- Avatar should appear and disappear exactly by real render duration.

## Internal Agent Layer

- `Random Agent` is now the canonical pre-monologue selector.
- File:
  - `/Users/akg/EVADAVA/CanvasGlassNew/docs/final-random-agent.txt`
- Purpose:
  - choose one episode-level `narrative_pattern`
  - choose `monologue_1..4_tone_variant`
  - choose `monologue_4_closing_mode`
  - suppress repetitive pattern reuse across recent episodes

- `Render Maker Agent` is now the canonical timing/raster assembly layer.
- File:
  - `/Users/akg/EVADAVA/CanvasGlassNew/docs/final-render-maker-agent.txt`
- Canonical timing formula:
  - `MON1 start = 0`
  - `MON2 start = Duration1`
  - `MON3 start = Duration1 + Duration2`
  - `MON4 start = Duration1 + Duration2 + Duration3 - 5 minutes`

## Episode Settings Layer

These must come from Google Sheet Settings and propagate through the full episode:

- `duration_1_min`
- `duration_2_min`
- `duration_3_min`

If these values change, they must update:
- monologue placement
- background windows
- playlist target duration
- total episode duration
- final render timing
- YouTube timestamps and description timing

## Desktop Shortcuts

- `/Users/akg/Desktop/CGNew_input`
- `/Users/akg/Desktop/CGNew_output`

## Next Recommended Step

1. Rebuild the avatar badge with the final gold-ring treatment from the zoomed preview logic.
2. Tighten the randomizer so visible events are rarer and spaced wider apart.
3. Keep all QR in the top-right information corner and reserve right-bottom for watermark.
4. Export the next cleaner master render after one more pass on motion subtlety.
