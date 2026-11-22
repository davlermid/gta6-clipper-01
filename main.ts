// gta6-clipper-01 entry (Node 22, standard library only).
// The entry is the YouTube video named in VIDEO.json; this program copies
// VIDEO.json from the repository root to /output/VIDEO.json for the gate.
//
// The clip was made by an AI agent in the uploaded sessions: it chose the
// moment from Rockstar's Grand Theft Auto VI Launch Trailer, decided the
// creative (hook explosion shot, Vice City montage, make.fun pitch in voice
// and on-screen text), cut and rendered the vertical clip with ffmpeg, and
// wrote this repository. The video is posted publicly on YouTube with the
// bounty's line and the entrant's play code in its description.
//
// Outside the grader's container:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'VIDEO.json'), join(OUTPUT_DIR, 'VIDEO.json'));
} catch (err) {
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
