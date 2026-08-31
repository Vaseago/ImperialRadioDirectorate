# CLAUDE.md

## What this is

**Imperial Radio Directorate.** A jukebox, built as a deliberate "vanity
project" (the user's own framing, 2026-08-21) - not filling a functional
gap the way IID/ISD/ILD do, worth building for its own sake. The 5th app
in the Imperial suite. Fully independent from its siblings: **zero EVE
ESI dependency, zero SDE dependency** - a pure local media player,
themed around EVE, with no EVE Online API dependency at all.

**The creative concept, SUPERSEDED 2026-08-24** (originally confirmed
2026-08-21, then deliberately redesigned - see "Real frontend rebuilt"
below for the full story): the device is now a **car-radio
reconstruction**, not a jukebox. The builder has heard, secondhand, of
a vehicle driven on paths he's never seen, carrying an item that caught
broadcast music/jingles/ads from the air, tuned by a knob to a
"frequency" - he has no concept of a car, a road, or radio itself, only
this one fragment. What he built is his own best guess at the receiving
item alone, freed of any vehicle it might have sat in: a wood-framed
black box with a circular tuning dial, nothing else. The
jukebox/disc-storage concept described in the rest of this section
historically (crown/body/plinth cabinet, disc-and-arm viewport,
disc-module) is **gone, fully replaced** - kept out of this file except
where a later section explicitly narrates the pivot, so a fresh reader
isn't misled by a description of a design that no longer exists. The
music-library architecture (AI-approximated "reconstructed audio,
fragmentary records") still applies unchanged - see the next section.

**Deferred/backlog ideas for this app live in `../TODO.md`'s "IRD"
heading**, not here and not in Claude's own memory (see `../TODO.md`'s
own intro) - check there for what's queued, and add new deferred ideas
there rather than tracking a separate list.

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

## Distribution

**Desktop-only-for-now (2026-08-21) - SUPERSEDED 2026-08-30, now also Pi-
hosted.** Originally: "this will be a desktop app only no 'webapp'
version, but leave the option open i just don't see hosting it on the pi
and accessing it from a different device at this time." That "leave the
option open" is exactly what paid off: `web/server.py` already bound
`0.0.0.0` same as the siblings, so a browser-reachable web server existed
"for free" the moment `ird_web_main.py` ran - no redesign was needed to
actually add Pi hosting once asked for directly ("the radio shall work
on the pi now"). A real public repo (github.com/Vaseago/ImperialRadioDirectorate)
was created and pushed the same day, `_supervisor/deploy/linux/install.sh`
was updated to clone/run it as a 4th app alongside IID/ISD/ILD (zero
`supervisor.py` changes needed - its own discovery was already fully
generic), and it's now confirmed running on the real Pi (port 8060,
`http://<pi-lan-ip>:8060/`) alongside the other three. Also gained
`--remote-url` on the desktop shell (ported from the sibling apps'
identical flag) so a desktop shortcut can wrap that Pi-hosted instance
instead of always spawning a local `ird_web_main.py` - see
`desktop_shell/app.py`'s own module docstring for the exact mechanics.

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
  isn't lost, not a green light to build now. **Confirmed 2026-08-24:
  once built, news snippets share `music_library_commercials/` with the
  ad jingles - NOT a separate folder/config/endpoint.** The commercials
  pool is already treated generically by `playNext()`'s ad-break logic
  (see "Stations, commercials, and static" below) - it doesn't care what
  KIND of non-station content it's picking, only that it's in that pool.
  So this feature needs zero new backend/config work when it's actually
  built: generate the TTS audio (same manual external flow as the ad
  jingle), drop the files into `music_library_commercials/` alongside
  whatever ad content is there, and they'll automatically get randomly
  mixed in through the exact same mechanism already shipped today.

## Real frontend rebuilt (2026-08-23 to 2026-08-24) - the tuner, not the jukebox

**First pass (2026-08-23, since fully replaced)**: a period jukebox
cabinet - crown/body/plinth, a disc-and-arm viewport, a side disc-module
- was built and shipped as the real frontend. **Real gotcha hit and
fixed during that build, still relevant**: browser HTTP caching of
static JS/CSS. `web/server.py` carries a `_NoCacheStaticFiles(StaticFiles)`
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

**Second pass (2026-08-24, the current, live design)**: the user
rejected the jukebox cabinet outright ("doesn't look good imo... lets
go with" the car-radio backstory - see "The creative concept" above)
and asked to rebuild around a completely different physical object: a
wood-framed black box holding one circular tuning dial, nothing else.
Iterated live via a single persistent Artifact
(`https://claude.ai/code/artifact/cccea29f-f98e-4d2e-a7f5-3fb4595ace7e`)
through several real corrections worth remembering:
- **A radial needle/"arm" pointing from the hub center looked "too
  strange"** - replaced with a small glowing dot that rides the arc at
  the tick radius (no visible shaft connecting it to center at all), so
  it reads as a tuning indicator LIGHT, not a gauge hand. `.needle`'s
  CSS comment in `style.css` records this explicitly - don't
  reintroduce a radial line here without re-litigating why it was
  removed.
- **No cabinet at all** - the black box IS the whole device, not housed
  in anything. A thin wood-grain `.wood-frame` border was added around
  it afterward (fits the "car radio in a wood dash" origin story), but
  that's decorative framing, not a cabinet with its own body/crown/side
  modules.
- **The hub is the only control** - no separate transport row, no track
  list. Clicking the RIGHT half of the hub steps to the next station,
  the LEFT half steps back, and dead CENTER toggles play/pause. This is
  real, live code (`web/static/js/app.js`'s `hub-hit` click handler,
  `svgPoint()` converting a real click to SVG-space coordinates via
  `getScreenCTM().inverse()`), not just the mockup.
- **No track list, ever** - each station plays a random pick from its
  own pool automatically (`pickRandomTrack()`, avoids immediately
  repeating the last pick), advancing on the real `<audio>` `ended`
  event - matching how an actual broadcast works, you tune to a
  station, you don't pick the song.

## Stations, commercials, and static (added 2026-08-24)

**"Station" is folder-per-station, not a hardcoded list.** A track's
top-level subfolder relative to its library dir becomes its station
name (`library/scanner.py`'s `_station_name()`), however deep the file
actually sits within that subfolder. A track with no subfolder (loose
at the library root - true of all 11 real files today) falls into a
shared `"General"` catch-all instead of being invisible. This was a
real, deliberate default chosen without asking first (documented as
such when built) - reversible any time by just adding subfolders under
`music_library/`. `web/static/js/app.js`'s `groupIntoStations()` builds
the dial's stations from whatever distinct `station` values come back
from `GET /api/library/tracks`, spreading them evenly across the arc
and assigning frequency numbers deterministically (alphabetical order,
88.1 to 108.3) - genuinely data-driven, not the mockup's fixed 4.

**A synthetic "All Stations" entry** is prepended whenever more than
one REAL station exists (never when there's only one - it would just
duplicate that one station), pulling randomly from every track
regardless of its real station.

**Commercials are a separate pool, never mixed into the station data.**
`config.COMMERCIALS_DIR` (default: a sibling `music_library_commercials/`
folder, NOT a subfolder of `MUSIC_LIBRARY_DIR` - that would make it look
like just another station to the folder-per-station logic) is scanned
independently into `app.state.commercials`, served via its own
`GET /api/library/commercials`. `web/static/js/app.js`'s `playNext()`
rolls a 25% chance (`AD_CHANCE`) to play a random commercial instead of
the next station pick, whenever the pool isn't empty and it isn't
already mid-commercial - real, working scheduling logic that simply
never fires today since `music_library_commercials/` is empty (no ad
audio exists yet - would need the same manual external-TTS flow as
`docs/AI_MUSIC_PROMPT.md`'s "Entertainment Box" ad jingle prompt).
`GET /api/library/tracks/{id}/stream` checks BOTH `app.state.tracks` and
`app.state.commercials` for a matching id, so a commercial streams
through the exact same endpoint a station track does.

**An empty library plays generated static, not silence.** If
`GET /api/library/tracks` comes back with zero stations, the dial still
shows "NO SIGNAL" and the hub's CENTER click still works - it starts a
real Web Audio API white-noise loop (`startStatic()`/`stopStatic()` in
`app.js`: a 2-second buffer of random samples via `AudioContext.createBuffer()`,
looped, at low gain) rather than nothing. Left/right are no-ops with
zero stations (nothing to step between), but center always works -
otherwise there'd be no way to ever hear the static at all.

**Real bugs found and fixed live, 2026-08-24, via the user's own
hands-on testing of the running app** (not caught by any automated
test, since these are UI-interaction bugs): (1) `tune()` originally
only started playback `if (playing)` was already true - meaning
changing station while paused did nothing audible at all. Fixed:
turning the dial is now itself a "play this now" action, unconditionally
setting `playing = true` and picking a fresh track, regardless of prior
state - a real radio always produces sound when tuned. (2) The initial
page-load call to `tune()` needed a separate `autoplay=false` path so
it DOESN'T try to auto-play on load (browsers block audio without a
real user gesture anyway, which would have desynced the "PLAYING" text
from actual silence) - `tune(index, autoplay)`'s second parameter exists
specifically for this one call site. (3) The hub's click handler
originally bailed out entirely `if (stations.length === 0)`, which would
have made the CENTER click (the only way to hear static) unreachable
too - fixed to only skip the left/right branches when there's nothing to
step between, never the center branch.

**Branding, added 2026-08-24**: with no cabinet/crown left, the device
had no visible name anywhere on it (only the `<title>` tag). Fixed by
etching "ENTERTAINMENT BOX" directly into the top of the `.wood-frame`
itself (`.frame-label` - a recessed/engraved text treatment: a color
darker than the surrounding wood plus a 1px light `text-shadow` below
to fake a carved highlight, no glow) rather than adding a separate
plaque or crown element - the wood border IS the branding surface now.

## Not yet built

- PWA polish (manifest/icons/service worker) - deferred until there's
  real iconography to ship, matching the sibling apps' own pattern.
- Radio news snippets between tracks (see "Deliberately deferred"
  above) - visual design phase is now done, so this is the natural next
  phase, but still not started without an explicit ask. Folder/scheduling
  decision already made (see that section) - shares
  `music_library_commercials/` with ad jingles, no new plumbing needed.
- Real commercial audio content - the scheduling mechanism is live (see
  above); `music_library_commercials/` now holds 6 real voice-over
  clips (moved 2026-08-25 from `music_library/`, where they'd been
  sitting mixed in with real music since 2026-08-23 - they were picked
  as regular station tracks ~55% of the time instead of going through
  the real 25% ad-roll until this move).
- **Old-time-radio drama stories - scoped 2026-08-25, not started.**
  `docs/AI_STORY_PROMPT.md` - Amarr Imperial Radio drama serials
  (Minmatar-aggression plots, in-universe pro-Amarr propaganda framing,
  single-narrator storyteller voice), same external-AI-generation
  pattern as `AI_MUSIC_PROMPT.md`. Written after the author asked about
  pulling similar AI-narrated stories from YouTube - declined (real
  copyright/ToS issue even for AI-written content, see that file's own
  "Why not just download the YouTube ones" section) - this is the safe,
  original-content alternative. Shares `music_library_commercials/`
  with the ad jingle and any future news snippets above, no new
  plumbing needed once real files exist.

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

## Verified live, 2026-08-24 (the current tuner frontend + stations/commercials/static)

Full backend suite: 15/15 checks pass across `tests/test_scanner.py`
(now 5 checks - added folder-per-station derivation, including the
nested-subfolder and loose-file-at-root cases) and
`tests/test_library_api.py` (now 3 checks - added the `station` field
on `/tracks` and the separate `/commercials` pool + its shared streaming
endpoint). Real, not mocked-away: `check_commercials_are_a_separate_pool_and_stream_correctly()`
uses two genuinely separate isolated temp dirs for `MUSIC_LIBRARY_DIRS`
vs `COMMERCIAL_DIRS`.

Frontend verified live via real DOM click dispatch against the running
`ird-test` server (port 18060, real 11-track library), not just code
review: initial page load shows "General" (the only real station right
now) tuned but correctly PAUSED, not auto-playing; clicking the right
half of the hub starts real playback (`paused: false`, `readyState: 4`,
a real track title) even though there's only one real station to step
within, confirming the "turning the dial always plays something" fix;
center click toggles pause/resume correctly, including the CSS `.paused`
class; the generated white-noise static (`startStatic()`/`stopStatic()`)
was directly invoked and confirmed producing a real `running` AudioContext
with an active buffer source, and confirmed reachable end-to-end through
`setPlaying(true)` when `stations.length === 0`, including the correct
"STATIC" / "NO SIGNAL" text swap.

Desktop shell re-verified against this exact frontend (not the earlier
jukebox one): launched `ird_desktop_main.py` for real, confirmed via the
spawned web server's own request log that the `QWebEngineView` loaded
`/`, `/static/css/style.css`, `/static/js/app.js`, `GET /api/library/tracks`,
and the new `GET /api/library/commercials` - all `200 OK`, zero errors.
Process tree cleaned up afterward (`Stop-Process` on the real PIDs found
via `Get-CimInstance Win32_Process`, not a blind `pkill` guess - the
first `pkill -f ird_desktop_main.py` attempt silently matched nothing
because the real process tree was `python3.exe` -> `python.exe`, not a
name `pkill` happened to match).
