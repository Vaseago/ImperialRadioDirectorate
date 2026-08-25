# Story prompt - Amarr Imperial Radio drama serial

Written 2026-08-25 alongside the volume/looping/ad-mix work, after the
author asked about pulling AI-narrated stories from YouTube for the
radio - declined (see below). Revised the same day once the real scope
became clear: these are meant to be **long-form told stories, roughly
an hour to an hour and a half spoken** - the kind of full serial drama
that filled the airwaves before television existed - not a short
between-track bumper. The first one was written directly, in full, by
Claude rather than handed off to an external generator - see "The first
story" below. This file's own prompt is kept as a template for either
approach on future stories: ask Claude to write another one directly
the same way, or run the prompt through an external AI text tool
yourself if you'd rather generate it that way.

## Why not just download the YouTube ones

Those videos - AI-narrated dramatic stories - are still somebody's
specific copyrighted upload (narration, editing, assembled production),
regardless of the writing itself being AI-generated, and YouTube's own
terms only permit downloading through its own official feature. Writing
new, original narration from scratch sidesteps that entirely - nothing
is extracted or reproduced from any existing video.

## The first story

**`docs/stories/the_reach_at_vharo.md`** - "The Reach at Vharo," roughly
9,400 words (~63-75 minutes spoken, depending on narration pace - a
measured, dramatic storyteller reads slower than a newsreader). Written
directly by Claude, not generated externally - fully original prose,
ready to paste straight into a text-to-speech tool as-is. Covers: a
quiet Amarr border mining platform, a Minmatar raiding captain with his
own real reasons (not a cardboard villain), a scout who infiltrates the
station beforehand, a convoy raid, a defense mounted by ordinary
station residents as much as by the Navy, and the station's own
memorial and aftermath once the guns stop. Framed throughout as a
told story - "you'll want to remember his name," "here's where it
turns" - the way an actual radio storyteller would talk to a listener
across an hour-long telling, not a plain prose narrative that happens
to be read aloud.

## The concept

**Format**: not a news bulletin, not a short bumper - a real **old-time
radio drama serial**, the kind that filled the airwaves before
television existed (Mercury Theatre, adventure serials, that whole
tradition), told at real length. A told STORY with scenes, tension, and
reported dialogue, narrated throughout by one consistent storyteller's
voice speaking to a listener - not a newsreader reading headlines, and
not plain third-person prose that only sounds like a narrator at the
very beginning and end. The narrator's voice should surface periodically
all the way through: direct address, asides, rhetorical framing
("you'll want to remember this name," "here's where it turns") -
enough that it consistently reads as being TOLD, not merely read.

**Antagonist**: not an invented alien faction - **Minmatar aggression**,
drawing on EVE Online's own real, much richer core rivalry (the Amarr
Empire's historical enslavement of the Minmatar, the Rebellion that
freed most of them, and the real ongoing hostility between the two
empires in EVE's own lore) rather than a generic invented threat. Keep
it inspired-by, not verbatim - original character names, ship names,
and specific incidents, not lines lifted from CCP's own published lore.

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
it. That said - "The Reach at Vharo" gives its Minmatar characters real
reasons and real moments of decency of their own (a raiding captain who
covers his crew's retreat at his own cost rather than fighting to the
last for a win; a navigator whose grief is treated as genuine, not
mocked) - a propaganda broadcast that makes its enemy a cardboard
monster is less convincing, not more, and reads as thinner fiction.
The one-sidedness is in whose side wins and whose cause the story
believes in, not in denying the other side any humanity at all.

## Prompt (for writing a new one - by Claude directly, or an external text generator)

Write a long-form old-time-radio-drama story, roughly 9,000-13,000
words (an hour to an hour and a half read aloud at a measured,
dramatic pace), narrated in-universe as an Amarr Imperial Radio serial
- the kind of scripted adventure drama that used to fill the airwaves
before television existed. One consistent narrator voice tells the
whole story directly to a listener, all the way through - not just at
the open and close - including reported dialogue ("the captain ordered
the fleet to hold position") rather than switching between separate
voice actors. Structure it in named chapters/sections with real scene
variety: establish an ordinary Amarr setting and its people first, then
a Minmatar raid or act of aggression against it, the defense mounted by
both military and ordinary civilian characters, a real turning point,
and a full aftermath/memorial section - don't resolve too quickly, the
length is meant to be used for real character depth and multiple named
figures on both sides, not padding.

The tone is confident, reverent, and unapologetically pro-Amarr - the
Empire is cast as the sole righteous, order-bringing force, and
Minmatar aggression as the disorder it puts down - but give the
Minmatar side real people with real, even sympathetic reasons of their
own; a one-note villain reads as weaker fiction, not stronger
propaganda. Build real tension and stakes before resolving in Imperial
victory and a closing note reaffirming order under the Emperor.

Invent original names for every system, ship, and character involved
on both sides - draw on EVE Online's real Amarr/Minmatar rivalry
(historical enslavement, the Rebellion, ongoing hostility) only as tone
and background, never verbatim lines or specific named lore events from
CCP's own published material. Write it to be READ ALOUD by a single
storyteller - real rhetorical rhythm, direct address to the listener
threaded throughout (not just bookending it), scene-setting language a
narrator would actually speak, no stage directions or camera-style
prose.

## Voice/narration prompt (for a TTS tool - ElevenLabs, etc.)

An authoritative, resonant male storyteller voice - formal, commanding,
faintly reverent, like an old-time radio drama narrator with total
confidence in how the story ends. Measured, deliberate pacing with real
dramatic timing - builds tension through the raid/conflict, then
settles into steady, triumphant certainty by the close. No music bed,
narration only (a music sting or sound-effect bed can be layered
separately later if wanted). Given the real length involved, most TTS
tools will need the text split into chapter-sized chunks and stitched
back together - `the_reach_at_vharo.md`'s own chapter breaks are
already sized for that.

## Notes

- Multiple stories with different invented casts/incidents/ships give
  real variety in rotation - ask for "a different incident and cast
  than before, same length and format" for follow-up stories.
- Drop finished narration files straight into `music_library_commercials/`
  - the existing 25% `AD_CHANCE` roll already mixes anything in that
  folder into rotation, no other setup needed (same mechanism already
  live for the "Entertainment Box" ad jingle). A full hour-plus story
  in the same rotation as a 20-second jingle is a real, deliberate
  mismatch worth being aware of - may be worth its own separate
  scheduling treatment (a dedicated "story hour" trigger rather than
  the same random ad-roll) if these become a regular feature; not
  built, not asked for yet.
- If a result reads too much like a neutral news article, or only
  sounds like a narrator at the very beginning and end, add "more like
  a spoken drama, narrator's voice present throughout, not a plain
  prose retelling" and regenerate - the in-universe bias and constant
  storytelling voice are the point, not something to soften.
- A real future enhancement, not built into this prompt yet: true
  multi-voice dialogue (separate TTS voices per character) instead of
  one narrator reporting dialogue - ElevenLabs and similar tools
  support this, worth exploring once the single-narrator version is
  working well.
