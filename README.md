# gta6-clipper-01 — "GTA 6's CRAZIEST shot — my AI agent made this for $0"

Entry for the make.fun bounty **gta6-clipper-01** ("Clip GTA 6 for the most YouTube views", $500, top 20 by views).

## The clip

- **Moment**: Rockstar Games' official *Grand Theft Auto VI Launch Trailer* (uploaded 2026-10-15, 86.8M views) —
  the freshest GTA 6 footage; the game released 2026-11-19.
- **Creative**: hook with the trailer's explosion shot ("GTA 6 IS FINALLY OUT"), a Vice City montage
  (night aerial + logo reveal, swamp, boat, club, police street, Jason & Lucia), and a closing pitch —
  spoken and on screen — that the clip was cut by an AI agent and that you can earn money making clips
  with AI on make.fun.
- **Format**: vertical 1080×1920, ~42 s, H.264 30 fps, word-by-word captions synced to narration,
  trailer audio ducked under the voice, loudness −16 LUFS.
- **Made by**: an AI agent in the uploaded sessions (moment selection via ffmpeg scene detection,
  narration via Piper TTS en-GB, cut and render via ffmpeg).

## Repository

- `main.ts` — Node 22, standard library only; copies `VIDEO.json` to `/output/VIDEO.json`.
- `VIDEO.json` — the public YouTube address of the clip (filled in after upload).
- `build_clip2.py` — the exact render script the agent ran.

## Upload requirements (per bounty rules)

- Post publicly on YouTube (Short or video) before the deadline (2026-11-23T01:00Z).
- Description must carry the line:
  `Made by my AI agent for a $500 bounty on make.fun, where you can earn money making clips with AI: https://make.fun/bounty/gta6-clipper-01`
  and the entrant's play code (or the code in the channel description).
- Keep the video public until results are out.

License: MIT.
