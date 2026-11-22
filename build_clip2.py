#!/usr/bin/env python3
"""Build gta6-clipper-01 vertical clip — low-memory two-stage version.

Stage 1: render each segment (vertical crop, fade in/out 0.15s) to seg files.
Stage 2: concat + overlays (hook text, pitch text, typewriter captions) + audio mix.
"""
import subprocess, textwrap, os

SRC = 'gta6-launch-trailer.mp4'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
OUT = 'gta6-clipper-v1-en.mp4'

SEGMENTS = [
    (67.9, 71.9), (14.5, 25.7), (25.7, 30.7), (32.1, 38.1),
    (41.7, 47.7), (62.5, 67.5), (67.9, 73.1),
]
FADE = 0.15

def run(cmd):
    print('>', ' '.join(cmd[:8]), '...')
    subprocess.run(cmd, check=True)

os.makedirs('segs', exist_ok=True)
durs = []
for i, (a, b) in enumerate(SEGMENTS):
    d = b - a
    durs.append(d)
    vf = (f"crop=ih*9/16:ih,scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,"
          f"fps=30,setsar=1,format=yuv420p,"
          f"fade=t=in:st=0:d={FADE},fade=t=out:st={d-FADE:.2f}:d={FADE}")
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', SRC,
         '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
         '-threads', '2', f'segs/seg{i}.mp4'])
    # audio bed per segment
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', SRC,
         '-vn', '-c:a', 'pcm_s16le', f'segs/seg{i}.wav'])

TOTAL = sum(durs)
print('total:', round(TOTAL, 2))

# concat list
with open('segs/list.txt', 'w') as f:
    for i in range(len(SEGMENTS)):
        f.write(f"file 'seg{i}.mp4'\n")
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'segs/list.txt',
     '-c', 'copy', 'segs/joined.mp4'])

# audio bed concat
with open('segs/alist.txt', 'w') as f:
    for i in range(len(SEGMENTS)):
        f.write(f"file 'seg{i}.wav'\n")
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'segs/alist.txt',
     '-c', 'copy', 'segs/bed.wav'])

# timeline offsets (no overlap now)
offsets, t = [], 0.0
for d in durs:
    offsets.append(t); t += d

NARR = [
    ('narrA.wav', 0.3, 'Grand Theft Auto Six is finally here! Thirteen years of waiting, and Vice City has never looked this good.', 7.047),
    ('narrB.wav', 31.5, 'This clip was cut by my AI agent. And on make dot fun, you can earn money making clips with AI. Link in the description!', 8.266),
]

def esc(s):
    return s.replace('\\', '\\\\').replace(':', '\\:').replace("'", "\\'").replace('%', '\\%')

def word_timings(text, start, total_dur):
    words = text.split()
    weights = [len(w) + 1 for w in words]
    tot = sum(weights)
    out, cur = [], start
    for w, wt in zip(words, weights):
        d = total_dur * wt / tot
        out.append((w, cur, cur + d)); cur += d
    return out

ov = []
ov.append(f"drawtext=fontfile={FONT}:text='GTA 6 IS FINALLY OUT':fontsize=92:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=300:enable='between(t,0.1,3.8)'")
ov.append(f"drawtext=fontfile={FONT}:text='WELCOME BACK TO VICE CITY':fontsize=64:fontcolor=white:borderw=4:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=320:enable='between(t,7.0,11.0)'")
pitch_start = offsets[-1] + 0.2
ov.append(f"drawtext=fontfile={FONT}:text='CUT BY MY AI AGENT':fontsize=76:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=280:enable='between(t,{pitch_start:.2f},{TOTAL:.2f})'")
ov.append(f"drawtext=fontfile={FONT}:text='EARN MONEY MAKING CLIPS WITH AI':fontsize=58:fontcolor=yellow:borderw=4:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=390:enable='between(t,{pitch_start:.2f},{TOTAL:.2f})'")
ov.append(f"drawtext=fontfile={FONT}:text='make.fun':fontsize=96:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=490:enable='between(t,{pitch_start:.2f},{TOTAL:.2f})'")

for fname, st, txt, nd in NARR:
    shown = []
    for w, ws, we in word_timings(txt, st, nd):
        shown.append(w)
        wrapped = textwrap.wrap(' '.join(shown), width=26)[-2:]
        t2 = '\\n'.join(esc(l) for l in wrapped)
        ov.append(f"drawtext=fontfile={FONT}:text='{t2}':fontsize=54:fontcolor=white:borderw=3:bordercolor=black:shadowcolor=black@0.7:shadowx=2:shadowy=2:line_spacing=8:x=(w-text_w)/2:y=1500:enable='between(t,{ws:.2f},{we:.2f})'")

fc = (f"[0:v]{','.join(ov)}[vout];"
      f"[1:a]volume=-22dB[bed];"
      f"[2:a]aresample=48000,adelay={int(NARR[0][1]*1000)}:all=1[na];"
      f"[3:a]aresample=48000,adelay={int(NARR[1][1]*1000)}:all=1[nb];"
      f"[bed][na][nb]amix=inputs=3:duration=first:dropout_transition=0:normalize=0,"
      f"loudnorm=I=-16:TP=-1:LRA=11[aout]")

run(['ffmpeg', '-y', '-v', 'error', '-i', 'segs/joined.mp4', '-i', 'segs/bed.wav',
     '-i', NARR[0][0], '-i', NARR[1][0], '-filter_complex', fc,
     '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-preset', 'veryfast',
     '-crf', '19', '-threads', '2', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000',
     '-ac', '2', '-movflags', '+faststart', OUT])
print('done:', OUT)
