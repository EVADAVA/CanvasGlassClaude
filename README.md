# CanvasGlassNew

This repository starts with a minimal secrets policy.

## Credentials and Tokens

- Store real secrets only in local environment files, CI secret storage, or your hosting platform's secret manager.
- Commit only `.env.example` with variable names and empty values.
- Never expose secrets to frontend bundles or commit them to Git.
- Use separate credentials for development, staging, and production.
- Rotate any token that has been pasted into chat, logs, screenshots, or commits.

## Local Development

1. Copy `.env.example` to `.env.local`.
2. Fill in real values in `.env.local`.
3. Keep `.env.local` out of version control.

## CI and Production

- GitHub Actions: use repository or environment secrets.
- Hosting: use the platform's encrypted secret storage.
- Prefer short-lived tokens where possible.

More detail is in `docs/security/secrets.md`.

## PD Image Prep

Use `scripts/prepare_pd_image.py` to convert a painting image into a base64 JPEG suitable for the PD Agent.

Example:

```bash
python3 scripts/prepare_pd_image.py /path/to/painting.png \
  --output ./artifacts/painting-1.pd.jpg \
  --base64-out ./artifacts/painting-1.pd.b64.txt
```

Defaults:
- outputs JPEG next to the source file as `<name>.pd.jpg`
- targets `<= 12 MB`
- enforces a hard limit of `<= 20 MB`
- writes base64 only when `--base64-out` is provided

## HeyGen

HeyGen credentials belong in `.env.local`.

Current project notes and verified API scope:

- `docs/heygen-api-scope.md`

Quick probe:

```bash
python3 scripts/heygen_probe.py
```
