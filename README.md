# Imperial Radio Directorate

A jukebox themed as if built by a distant-future EVE-universe engineer
who only knows about "20th-century jukeboxes" from fragmentary
historical records - a 1950s-diner aesthetic reconstructed with alien
tech, getting the details charmingly wrong. Same conceit applies to the
music itself: rather than the real EVE soundtrack (never extracted from
the game client - see `THIRD_PARTY_NOTICES.md`), the library holds
AI-generated original ambient music approximating what "ancient jukebox
music" might have sounded like.

Built as a "vanity project" - the 5th Imperial app, alongside Imperial
Industry/Skill/Logistic Directorate, built for its own sake rather than
to fill a functional gap. Desktop app only for now (see `CLAUDE.md`).

## Status

Core playback (backend + minimal frontend + desktop shell) is built and
live-verified. The alien-retro visual design and the in-universe "radio
news" snippet idea are both real, scoped-but-not-yet-built future
phases - see `CLAUDE.md`.

## Requirements

- Python 3.11+
- `pip install -r requirements.txt`

## Run

```
python3 ird_web_main.py       # browser companion, http://localhost:8060/
python3 ird_desktop_main.py   # native desktop window
```

## Adding music

Drop audio files (`.mp3`, `.ogg`, `.oga`, `.flac`, `.wav`, `.m4a`,
`.aac`) into `music_library/`, then click "Rescan Library" in the app.
See `docs/AI_MUSIC_PROMPT.md` for a ready-to-use AI-music-generation
prompt to populate it with original tracks.
