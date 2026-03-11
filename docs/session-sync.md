# CanvasGlassNew Session Sync

Last updated: 2026-03-10

## Read This First

After restart, read this file first:

- [/Users/akg/EVADAVA/CanvasGlassNew/docs/session-sync.md](/Users/akg/EVADAVA/CanvasGlassNew/docs/session-sync.md)

Then, if needed:

- [/Users/akg/EVADAVA/CanvasGlassNew/docs/project-model.md](/Users/akg/EVADAVA/CanvasGlassNew/docs/project-model.md)

## Canonical Project Path

- `/Users/akg/EVADAVA/CanvasGlassNew`

## Current Video State

- Current 15-minute master:
  - `/Users/akg/EVADAVA/CanvasGlassNew/output/video_render_test1_Klimt_final_15min_tight.mp4`
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

## HeyGen / Monologue Notes

- `MON1..MON4` are generated and rendered.
- Template path works.
- Actual rendered monologue duration must be treated as a system parameter for final assembly.
- Avatar should appear and disappear exactly by real render duration.

## Desktop Shortcuts

- `/Users/akg/Desktop/CGNew_input`
- `/Users/akg/Desktop/CGNew_output`

## Next Recommended Step

1. Rebuild the avatar badge with the final gold-ring treatment from the zoomed preview logic.
2. Add one gallery ambience track under the master at very low level.
3. Export the next clean master render.
