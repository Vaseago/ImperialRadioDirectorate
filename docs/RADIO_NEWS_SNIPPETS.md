# Radio news snippets - deferred feature

**Status: idea only, NOT built.** Raised by the user 2026-08-21, fits
this app's own name better than pure music playback does - "Imperial
**Radio** Directorate," not "Imperial Jukebox Directorate." A real radio
station has news/talk breaks between songs; short, dry, in-universe EVE
flavor snippets (market/corporate news, wry references to real EVE
phenomena like AFK freighter ganking) interspersed with music tracks
would fit the theme better than straight-through music alone.

Explicitly scoped as a LATER phase, after V1's core playback (done) and
the visual design phase (not yet done) - see `CLAUDE.md`'s "Deliberately
deferred" section. **Do not start building this without the user
explicitly asking** - confirmed again 2026-08-23. This file exists so
the idea, the example snippets, and the playback mechanic aren't lost
between sessions, not as a green light to implement.

## Playback mechanic (confirmed with the user, 2026-08-23)

Snippets play **between tracks**, at **random intervals** - not on a
fixed schedule (e.g. not "every 3 tracks") and not between every single
track. When a break is triggered, **one random snippet** is picked from
the pool below and played/shown before the next track starts.

## Open questions (not yet resolved - see CLAUDE.md's fuller writeup)

1. **Audio vs. text-only.** Real voiced snippets would need their own
   external-AI-generation flow (a TTS prompt document, same
   "Claude can't generate audio itself" constraint as `AI_MUSIC_PROMPT.md`),
   whereas a text-only overlay shown during a short pause/jingle is a
   much smaller, purely-in-app lift with zero external dependency.
   Leaning toward starting text-only.
2. **What "random interval" means concretely** - e.g. a random chance
   checked at the end of each track, vs. a random N-tracks-until-next-break
   counter. Not yet decided.
3. **Static vs. varied over time** - static (written once, like the pool
   below) is simpler and enough for a first version.

## Snippet pool

In-universe EVE flavor, playfully blending real EVE humor (AFK
freighter ganking, gate camps, capsuleer culture) with the user's own
Imperial Apps as in-universe "corporations." Deadpan corporate-news
voice - short, dry, no punchline telegraphed.

Drafted 2026-08-21 (see the original plan file,
`C:\Users\vasea\.claude\plans\mellow-petting-stardust.md`, for where
these first appeared):

1. "Local news: a freighter has been reported destroyed while idling at
   a gate in high-sec. Investigators cite 'undocking' as a contributing
   factor."
2. "Imperial Industry Directorate shares dipped 3% this cycle amid
   rumors of a hostile blueprint acquisition. Analysts remain
   unconcerned."
3. "A capsuleer was seen undocking a freighter without an escort today.
   Local news has nothing further to add."

Drafted 2026-08-23:

4. "Local news: a Rorqual was reported destroyed this morning while its
   pilot was reportedly 'just going to the bathroom real quick.'
   Corporation leadership has opened an internal review."
5. "Imperial Logistic Directorate confirmed today that its jump-route
   planner has never once been consulted before an actual jump. 'We
   just like knowing the number,' one pilot explained."
6. "A capsuleer in Providence was successfully talked out of undocking
   today by three separate corpmates, local intelligence, and a brief
   moment of clarity. He undocked anyway."
