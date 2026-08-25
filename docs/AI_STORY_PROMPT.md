# AI story prompt - Amarr Imperial Radio drama serial

Written 2026-08-25 alongside the volume/looping/ad-mix work, after the
author asked about pulling AI-narrated stories from YouTube for the
radio - declined (see below), this is the safe alternative: a prompt
for generating wholly ORIGINAL narrated fiction, run through an AI tool
by the author themselves, same arm's-length pattern
`AI_MUSIC_PROMPT.md` already established for the music. Meant for
`music_library_commercials/` alongside the ad jingle and any future
short news snippets - same pool, same playback mechanism, no new code.

## Why not just download the YouTube ones

Those videos - AI-narrated dramatic stories - are still somebody's
specific copyrighted upload (narration, editing, assembled production),
regardless of the writing itself being AI-generated, and YouTube's own
terms only permit downloading through its own official feature.
Generating new, original narration from a prompt like this one
sidesteps that entirely - nothing is extracted or reproduced from any
existing video.

## The concept

**Format, corrected 2026-08-25**: not a news bulletin - a real
**old-time radio drama**, the kind that filled the airwaves before
television existed (Mercury Theatre, adventure serials, that whole
tradition). A told STORY with scenes, tension, and reported dialogue,
narrated by one voice - not a newsreader reading headlines.

**Antagonist, corrected 2026-08-25**: not an invented alien faction -
**Minmatar aggression**, drawing on EVE Online's own real, much richer
core rivalry (the Amarr Empire's historical enslavement of the
Minmatar, the Rebellion that freed most of them, and the real ongoing
hostility between the two empires in EVE's own lore) rather than a
generic invented threat. Keep it inspired-by, not verbatim - original
character names, ship names, and specific incidents, not lines lifted
from CCP's own published lore.

**In-universe framing, not a neutral retelling**: this is still Amarr
Imperial Radio's OWN broadcast - a state media arm of a real theocratic
empire, so of course it casts its own empire as the righteous,
order-bringing hero and Minmatar raiders/aggressors as the disorder
being met. That's not a simplification, it's an accurate one: an
Imperial propaganda broadcast would frame things exactly this way
regardless of how morally complicated the real history between these
two empires actually is. Leaning into that one-sidedness (rather than
writing a neutral "both sides" account) is what makes it read as a real
in-universe broadcast, not generic narration with an Amarr sticker on
it. Keep the history itself referenced only at a light, scene-setting
level (old grievances, a raid, a rescue, a siege) - the drama is the
point, not a history lecture.

## Prompt (for a text/story generator - Claude, GPT, etc.)

Write a short old-time-radio-drama story (500-800 words), narrated
in-universe as an Amarr Imperial Radio serial - the kind of scripted
adventure drama that used to fill the airwaves before television
existed. One narrator voice tells the whole story, including reported
dialogue ("the captain ordered the fleet to hold position") rather than
switching between separate voice actors. The plot centers on a
Minmatar raid or act of aggression against an Imperial system, ship, or
outpost, and the Imperial Navy's disciplined, faithful response. The
tone is confident, reverent, and unapologetically pro-Amarr - the
Empire is cast as the sole righteous, order-bringing force, and
Minmatar aggression as the disorder it puts down. Build real tension
and stakes before resolving in Imperial victory and a closing note
reaffirming order under the Emperor.

Invent original names for the system, ships, and any named Imperial
officers or Minmatar raiders involved - draw on EVE Online's real
Amarr/Minmatar rivalry (historical enslavement, the Rebellion, ongoing
hostility) only as tone and background, never verbatim lines or
specific named lore events from CCP's own published material. Write it
to be READ ALOUD by a single storyteller - real rhetorical rhythm,
scene-setting language a narrator would actually speak, no stage
directions or camera-style prose.

## Voice/narration prompt (for a TTS tool - ElevenLabs, etc.)

An authoritative, resonant male storyteller voice - formal, commanding,
faintly reverent, like an old-time radio drama narrator with total
confidence in how the story ends. Measured, deliberate pacing with real
dramatic timing - builds tension through the raid/conflict, then
settles into steady, triumphant certainty by the close. No music bed,
narration only (a music sting or sound-effect bed can be layered
separately later if wanted).

## Notes

- Keep each story self-contained and short (a few minutes spoken) -
  matches how the existing ad jingle sits between station tracks,
  rather than demanding a long sit-through.
- Multiple stories with different invented officers/ships/incidents
  give real variety in rotation - regenerate with "a different
  incident and cast than before" for follow-up batches.
- Drop finished narration files straight into `music_library_commercials/`
  - the existing 25% `AD_CHANCE` roll already mixes anything in that
  folder into rotation, no other setup needed (same mechanism already
  live for the "Entertainment Box" ad jingle).
- If a result reads too much like a neutral news article rather than a
  told story, add "more like a spoken drama, less like a report" and
  regenerate - the in-universe bias and storytelling voice are the
  point, not something to soften.
- A real future enhancement, not built into this prompt yet: true
  multi-voice dialogue (separate TTS voices per character) instead of
  one narrator reporting dialogue - ElevenLabs and similar tools
  support this, worth exploring once the single-narrator version is
  working well.
