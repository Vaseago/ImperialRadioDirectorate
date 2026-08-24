# CLAUDE.md

## What this is

**Imperial Radio Directorate.** A jukebox, built as a deliberate "vanity
project" (the user's own framing, 2026-08-21) - not filling a functional
gap the way IID/ISD/ILD do, worth building for its own sake. The 5th app
in the Imperial suite. Fully independent from its siblings: **zero EVE
ESI dependency, zero SDE dependency** - a pure local media player,
themed around EVE, with no EVE Online API dependency at all.

**The creative concept** (confirmed with the user, 2026-08-21): visually
and sonically, a 1950s American diner-style jukebox reimagined as if
built by someone in the EVE-future who only knows about "jukeboxes" from
fragmentary historical records, reconstructing one using their own era's
alien tech and getting the details charmingly wrong (holographic
emitters instead of glass tubes, force-field-style buttons, proportions
that never quite fit a human). The visual design phase (not yet built -
see "Not yet built" below) applies this to the UI; the music-library
design already applies it to the AUDIO too - see the next section.

## Legal grounding (read before touching the music library)

This app **never extracts, scrapes, or derives audio from the installed
EVE Online client** - CCP's Third Party Policies explicitly ban this
("cache scraping," EULA §9.C), actively enforced with real bans. Full
research trail: the `imperial-radio-directorate-idea` memory (this
project's Claude Code memory system), resolved 2026-08-20.

**Safe sources, and why the architecture is generic rather than
AI-specific**: (a) AI-generated ORIGINAL music (not sampled from
anything) - the V1 focus, see `docs/AI_MUSIC_PROMPT.md` for a real,
already-researched generation prompt; (b) the user's own legitimately-
purchased/owned audio files (e.g. CCP's own official Bandcamp store),
added via a second folder - NOT built into the default flow yet, but the
library scanner (`library/scanner.py`) works on ANY folder of audio
files, so this needs zero redesign later, just pointing
`config_overrides.json`'s `extra_music_dirs` at a real folder. CD-drive
ripping was explicitly considered and deferred - see "Deliberately
deferred" below.

This ties the legal-safety design to the creative concept: the device's
own music library isn't the real historical soundtrack, it's the
device's own AI-approximated reconstruction of what "ancient jukebox
music" might have sounded like from fragmentary records - not a
coincidence, the same "alien reconstruction" conceit applied to both the
visuals and the audio.

## Architecture (mirrors IID/ISD/ILD's own pattern, minus everything ESI/SDE)

- **`config.py`** - `MUSIC_LIBRARY_DIR`/`MUSIC_LIBRARY_DIRS`,
  `WEB_PORT` (8060, next unused slot after IID 8000/8010, ILD 8020/8030,
  ISD 8040/8050), `DATA_DIR`. **Key decision**: the music library is
  deliberately NOT `DATA_DIR`-derived - it's read-only, shared
  identically by the web service and any desktop shell instance, same
  reasoning as the sibling apps' own `SHARED_SDE_DIR`. Nothing here ever
  WRITES to the library, so there's no whole-file-save race and no
  per-client-id credential to isolate - the two real reasons the sibling
  apps isolate `DATA_DIR` per-instance at all. This means `config.py`'s
  "get `DATA_DIR` right" surface is much smaller than its siblings' -
  really just `config_overrides.json`.
- **`library/models.py`** / **`library/scanner.py`** - pure domain
  logic, no web/ dependency, mirrors `sde/`/`planner/`/`logistics/`'s
  separation-of-concerns principle in the sibling apps.
  `scan_library_dirs()` walks each configured dir, reads tags via
  `mutagen`, falls back to a cleaned-up filename when tags are missing
  (the "reconstructed audio, fragmentary records" framing paying off
  functionally). Track ID = `sha1(relative_path)[:16]` - stable across
  rescans, changes on rename (documented, accepted simplification). **No
  database** - `app.state.tracks` populated fresh at lifespan startup
  and on explicit `POST /api/library/rescan`, matching the sibling
  apps' "no over-engineered persistence" posture; a personal music
  library trivially fits in memory.
- **`web/routers/library.py`** - `GET /api/library/tracks` (list),
  `GET /api/library/tracks/{id}/stream` (plain `FileResponse` - Range-
  request support for seeking comes free from Starlette's own
  implementation, verified directly against the installed version's
  source, not assumed), `POST /api/library/rescan` (CSRF-guarded via
  `web/security.py`, same `require_same_origin_header` mechanism as the
  sibling apps, header renamed `X-IRD-Request`).
- **`web/server.py`** / **`ird_web_main.py`** - the two gotchas that
  already bit ISD/ILD for real (see `../CROSS_APP_ISSUES.md`), both
  avoided from day one here: `sys.frozen`-gated template/static path
  resolution, and `uvicorn.run(app, ...)` with the real imported object,
  never the `"web.server:app"` string form.
- **`desktop_shell/app.py`** - simpler than ISD/ILD's own shells, no ESI
  client ID/callback to register at all. Own port (8070), own `DATA_DIR`
  (`Imperial Radio Directorate Desktop`), deliberately does NOT override
  `MUSIC_LIBRARY_DIR` so it shows the identical library with zero
  duplication.

## Distribution (confirmed with the user, 2026-08-21)

**Desktop app only for now** - the user's own words: "this will be a
desktop app only no 'webapp' version, but leave the option open i just
don't see hosting it on the pi and accessing it from a different device
at this time." This needed zero special design - `web/server.py` binds
`0.0.0.0` same as the siblings, so a browser-reachable web server exists
"for free" the moment `ird_web_main.py` runs; the user just isn't
building/running an NSSM service or a Pi install path for it. Don't add
Pi/web-installer packaging work without the user asking first.

## Deliberately deferred (don't build without asking first)

- **CD-drive ripping** - considered and explicitly deferred. The user's
  own words: "if it can't read from cd. then we skip. most of my music
  at this point is digital anyhow sitting in a directory on my pc." A
  real, meaningfully bigger technical lift than file playback (Windows
  exposes audio CDs as tiny `.cda` placeholder files, not playable audio
  - a real rip needs digital audio extraction via a dedicated library/
  tool; browsers have zero access to raw CD drives at all, so it would
  need native OS-level handling in the desktop shell specifically). Only
  worth attempting if the user asks, and only if it turns out
  technically practical.
- **In-universe "radio news" snippets between tracks** - a real, good
  idea raised by the user mid-build 2026-08-21 (fits "Radio Directorate"
  better than pure music), with example snippets already drafted (see
  the plan file's own dedicated section,
  `C:\Users\vasea\.claude\plans\mellow-petting-stardust.md`, "Future
  idea... in-universe radio news snippets"). Explicitly scoped as a
  LATER phase, after the visual design phase - captured so the idea
  isn't lost, not a green light to build now.

## Real jukebox frontend shipped (2026-08-23) - "The One Real Upgrade"

The bare/functional-first frontend described as "not yet built" below
is done. The final visual design (arrived at through many rounds of
Artifact-hosted iteration, converging on a period jukebox cabinet whose
exterior reads as function-driven, not a copied reference - see the
`imperial-radio-directorate-idea` memory for the full design story) is
now the real, live `web/templates/index.html`/`web/static/css/style.css`/
`web/static/js/app.js` - cabinet crown/body/plinth, a live disc-and-arm
`.window` viewport (`.arm-pivot`'s `.spinning` class toggles with real
`player.paused` state), a 12-column pixel-matrix "rain" visualizer, real
prev/play-pause/next transport, and a side `.disc-module` connected via
a `.bracket`. Crown text still literally reads "IMPERIAL RADIO," not yet
updated to "Entertainment Box" (the confirmed official in-universe
product name per `docs/AI_MUSIC_PROMPT.md`'s ad-jingle section) - an
open, not-yet-decided question, not an oversight.

**Real gotcha hit and fixed during this build: browser HTTP caching of
static JS/CSS.** `web/server.py` gained a `_NoCacheStaticFiles(StaticFiles)`
subclass forcing `Cache-Control: no-store` on every `/static/*` response
- plain `StaticFiles` caches normally, which silently served a stale
`app.js` after real on-disk edits during development. **The debugging
trap worth remembering**: an explicit `fetch(url, {cache: 'no-store'})`
probe bypasses the browser's disk cache and will report the CORRECT,
current file even while the page's own real `<script src>` tag is still
loading a STALE cached copy underneath - the two don't share the same
cache-bypass behavior, so "my no-cache fetch shows the right content"
does NOT prove the live page is running the right content. A disk-cache
entry written before the `no-store` fix was deployed also persists
across brand-new tabs in the same browser profile/session - only a
genuinely fresh browser session (not just a fresh tab) proved the fix
actually worked. If a code change ever again appears to have "no
effect" despite the file on disk being correct, suspect this class of
bug before suspecting the code itself.

## Not yet built

- PWA polish (manifest/icons/service worker) - deferred until there's
  real iconography to ship, matching the sibling apps' own pattern.
- Radio news snippets between tracks (see "Deliberately deferred"
  above) - visual design phase is now done, so this is the natural next
  phase, but still not started without an explicit ask.

## Verified live, 2026-08-21 (not just "compiles")

Real automated tests actually run (not just written):
`tests/test_scanner.py` (metadata extraction, filename fallback,
unsupported-extension skip, track-ID stability/rename behavior, missing-
dir handling) and `tests/test_library_api.py` (FastAPI TestClient
against a real isolated library dir - list, full stream, a genuine
`Range: bytes=0-99` request confirmed returning real `206`/
`Content-Range`/exact byte count, 404 on unknown track, CSRF guard on
rescan) - all PASS. Frontend verified live in an actual browser against
the real running server: loaded a synthetic test track, clicked to play,
confirmed via direct JS inspection the `<audio>` element was genuinely
playing (`paused: false`, `readyState: 4`, `currentTime` actively
advancing), zero console errors. Desktop shell verified live too: the
spawned web-server subprocess and the `QWebEngineView`'s own real HTTP
requests (page load, static assets, API call) all confirmed via the
process's own log output.

## .mp4 support (added 2026-08-23) + real files verified live

`config.SUPPORTED_AUDIO_EXTENSIONS` gained `.mp4` after the user's
actual first batch of AI-generated tracks turned out to be plain `.mp4`
files - the exact same MP4 container `.m4a` already reads via mutagen's
`EasyMP4` class, so the scanner needed zero new parsing logic, just the
extension added. **Verified directly, not assumed, that these real
files carry an actual H.264 video track alongside the AAC audio** (raw
byte-scan for `vide`/`soun` handler atoms, not just a cover-art image) -
so `web/routers/library.py` gained an explicit `.mp4 -> audio/mp4` MIME
override (`_MIME_TYPE_OVERRIDES`), since Python's stdlib `mimetypes`
guesses `video/mp4` for this extension, which is wrong for a track meant
to play via an `<audio>` element.

**The user's own first 5 real tracks were then converted to `.m4a`
anyway** (their own call, given the choice) - stripped of the
unnecessary video track via a portable `imageio-ffmpeg` binary
(`-vn -c:a copy`, a lossless remux, no re-encoding since the audio codec
was already AAC), shrinking the library from ~15MB to ~4.5MB with zero
quality loss and all tags/duration preserved exactly. The `.mp4` support
itself was kept rather than reverted - it's real, tested, and covers any
FUTURE similarly-exported file dropped in without conversion, at zero
ongoing cost.

Verified live end-to-end against the user's real files (not synthetic
fixtures) via the root-level `ird-test` launch config
(`../.claude/launch.json`, port 18060): `GET /api/library/tracks` lists
all 11 real tracks (5 music + 6 ElevenLabs voice-over test clips),
playback of a real converted `.m4a` track confirmed genuinely playing
(`paused: false`, `readyState: 4`, `currentTime` advancing, correct
30.77s duration), and a real `Range: bytes=0-999` request against it
returned `206`/`Content-Type: audio/mp4`/correct `Content-Range`.
