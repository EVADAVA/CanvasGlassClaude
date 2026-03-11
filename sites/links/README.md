Links Site

Purpose:
- restore `links.evadava.com` from inside `CanvasGlassNew`
- host episode-level and painting-level landing routes
- act as the canonical QR redirect/landing surface for Canvas & Glass

Current route model:
- `/`
- `/paintings`
- `/paintings/<episode>_<painting>`

Reserved painting slugs currently loaded from:
- `../../docs/reserved_painting_routes.json`

Deploy target:
- Cloudflare Pages or equivalent static hosting

Notes:
- TikTok/legal pages for `evadava.com` remain separate and currently live from the `LEGOLOVER` project.
- This site is only for `links.evadava.com`.
