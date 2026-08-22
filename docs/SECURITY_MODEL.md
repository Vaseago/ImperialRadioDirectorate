# Security model

`web/` is an unauthenticated, LAN-wide trusted-network app, same posture
as the sibling Imperial apps - see `../SHARED_ARCHITECTURE.md`. Every
route is unauthenticated. The one state-changing route,
`POST /api/library/rescan`, is CSRF-guarded via `web/security.py`'s
`require_same_origin_header` - a bare cross-site HTML form cannot set
the required `X-IRD-Request` header, so it can't trigger a rescan.

Unlike the sibling apps, this one has no ESI tokens, no SDE, and no
git-pull "check for update" route to worry about - the attack surface
here is genuinely smaller: an unauthenticated LAN device can view the
track list and stream audio files from the configured library
directories, and trigger a rescan. Nothing here reads or writes
anything outside the configured `MUSIC_LIBRARY_DIRS` and
`DATA_DIR/config_overrides.json`.
