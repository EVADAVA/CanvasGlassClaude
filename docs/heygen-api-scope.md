## HeyGen API Scope

Verified against official HeyGen documentation and live account access on March 10, 2026.

### Local config

Use local environment variables only:

- `HEYGEN_API_KEY`
- `HEYGEN_TALKING_PHOTO_ID`
- `HEYGEN_VOICE_ID` (optional until voice is pinned)

`HEYGEN_API_KEY` and `HEYGEN_TALKING_PHOTO_ID` are stored locally in `.env.local` for this project.

### What is confirmed working

Official docs reviewed:

- [List avatars v2](https://docs.heygen.com/reference/list-avatars-v2)
- [List voices v2](https://docs.heygen.com/reference/list-voices-v2)
- [Create an avatar video v2](https://docs.heygen.com/reference/create-an-avatar-video-v2)
- [Get video status](https://docs.heygen.com/reference/get-video-status)
- [Webhook events](https://docs.heygen.com/docs/webhook-events)
- [Streaming avatars](https://docs.heygen.com/docs/streaming-avatars)

Live API verification from this project:

- `GET /v2/avatars` works with the current key.
- `GET /v2/voices` works with the current key.
- The configured ID `5fdb42130a58494a8be5e0770f9bc7ff` resolves as a `talking_photo_id`, not a standard `avatar_id`.
- Account scope currently exposes:
  - `1289` studio avatars
  - `5661` talking photos
  - `2311` voices
- The account includes custom voices named `Oleksandr Kuguk`.
- Those sampled custom voices report `support_pause: true`.

### What that means for CanvasGlassNew

The current configured visual identity should be treated as:

- `character.type = talking_photo`
- `character.talking_photo_id = HEYGEN_TALKING_PHOTO_ID`

Do not send this ID as a plain `avatar_id` unless the configured asset changes.

### Practical API capabilities we can use now

1. Account discovery
- list available studio avatars
- list talking photos
- list voices
- detect whether a configured ID is an avatar or a talking photo

2. Video generation
- create async avatar videos from text
- pair a selected character with a chosen voice
- submit one monologue per render job
- poll job status until completion

3. Delivery plumbing
- use webhooks for render completion and failure
- store returned video IDs and download URLs in episode state

4. Real-time path
- use Streaming Avatars for live or interactive presentation if we later want a conversational front end

### Current safe implementation path

For CanvasGlassNew, the lowest-risk integration is:

1. generate `mon1_heygen.txt`, `mon2_heygen.txt`, `mon3_heygen.txt`
2. normalize pause cues if needed
3. submit one HeyGen render job per monologue
4. poll `get video status`
5. save returned video URLs into the episode output folder or sheet state

### Things not yet fixed in project code

- no pinned `HEYGEN_VOICE_ID` yet
- no render script yet
- no webhook receiver yet
- no project-side normalization layer from `[pause 800ms]` cues into final HeyGen payload rules

### Probe command

Use this from the project root:

```bash
python3 scripts/heygen_probe.py
```

Optional:

```bash
python3 scripts/heygen_probe.py --voice-name "Oleksandr Kuguk"
```

### Immediate next step

Build a `scripts/heygen_render_monologue.py` helper that:

- loads `.env.local`
- accepts `--script-file`
- accepts optional `--voice-id`
- auto-detects `avatar` vs `talking_photo`
- submits a render job
- polls until success or failure
- writes a JSON receipt into `output/heygen/`
