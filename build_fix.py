#!/usr/bin/env python3
"""Stage 2 fix: overlays via textfile (correct newlines), smaller hook text,
two-pass loudnorm to -16 LUFS. Reuses segs/joined.mp4 + segs/bed.wav."""
import subprocess, textwrap, os, json

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
OUT = 'gta6-clipper-v1-en.mp4'
TOTAL = 42.4
os.makedirs('txt', exist_ok=True)

NARR = [
    ('narrA.wav', 0.3, 'Grand Theft Auto Six is finally here! Thirteen years of waiting, and Vice City has never looked this good.', 7.047),
    ('narrB.wav', 31.5, 'This clip was cut by my AI agent. And on make dot fun, you can earn money making clips with AI. Link in the description!', 8.266),
]

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
# hook: two lines, fits 1080 width
open('txt/hook.txt', 'w').write('GTA 6 IS\nFINALLY OUT')
ov.append(f"drawtext=fontfile={FONT}:textfile=txt/hook.txt:fontsize=110:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:line_spacing=10:x=(w-text_w)/2:y=260:enable='between(t,0.1,3.8)'")
open('txt/mid.txt', 'w').write('WELCOME BACK\nTO VICE CITY')
ov.append(f"drawtext=fontfile={FONT}:textfile=txt/mid.txt:fontsize=72:fontcolor=white:borderw=4:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:line_spacing=8:x=(w-text_w)/2:y=300:enable='between(t,7.0,11.0)'")
pitch_start = 37.4
open('txt/p1.txt', 'w').write('CUT BY MY AI AGENT')
ov.append(f"drawtext=fontfile={FONT}:textfile=txt/p1.txt:fontsize=72:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=280:enable='between(t,{pitch_start},{TOTAL})'")
open('txt/p2.txt', 'w').write('EARN MONEY MAKING\nCLIPS WITH AI')
ov.append(f"drawtext=fontfile={FONT}:textfile=txt/p2.txt:fontsize=64:fontcolor=yellow:borderw=4:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:line_spacing=8:x=(w-text_w)/2:y=390:enable='between(t,{pitch_start},{TOTAL})'")
open('txt/p3.txt', 'w').write('make.fun')
ov.append(f"drawtext=fontfile={FONT}:textfile=txt/p3.txt:fontsize=96:fontcolor=white:borderw=5:bordercolor=black:shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-text_w)/2:y=570:enable='between(t,{pitch_start},{TOTAL})'")

n = 0
for fname, st, txt, nd in NARR:
    shown = []
    for w, ws, we in word_timings(txt, st, nd):
        shown.append(w)
        wrapped = textwrap.wrap(' '.join(shown), width=26)[-2:]
        path = f'txt/cap{n}.txt'
        open(path, 'w').write('\n'.join(wrapped))
        ov.append(f"drawtext=fontfile={FONT}:textfile={path}:fontsize=54:fontcolor=white:borderw=3:bordercolor=black:shadowcolor=black@0.7:shadowx=2:shadowy=2:line_spacing=8:x=(w-text_w)/2:y=1500:enable='between(t,{ws:.2f},{we:.2f})'")
        n += 1

fc = (f"[0:v]{','.join(ov)}[vout];"
      f"[1:a]volume=-22dB[bed];"
      f"[2:a]aresample=48000,adelay={int(NARR[0][1]*1000)}:all=1[na];"
      f"[3:a]aresample=48000,adelay={int(NARR[1][1]*1000)}:all=1[nb];"
      f"[bed][na][nb]amix=inputs=3:duration=first:dropout_transition=0:normalize=0[aout]")

subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'segs/joined.mp4', '-i', 'segs/bed.wav',
                '-i', NARR[0][0], '-i', NARR[1][0], '-filter_complex', fc,
                '-map', '[vout]', '-map', '[aout]', '-c:v', 'libx264', '-preset', 'veryfast',
                '-crf', '19', '-threads', '2', '-c:a', 'aac', '-b:a', '320k', '-ar', '48000',
                '-ac', '2', 'segs/pre.mp4'], check=True)
print('stage2a done')

# loudnorm pass 1: measure
r = subprocess.run(['ffmpeg', '-i', 'segs/pre.mp4', '-af', 'loudnorm=I=-16:TP=-1:LRA=11:print_format=json',
                    '-f', 'null', '-'], capture_output=True, text=True)
j = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
print('measured:', j['input_i'], j['input_tp'], j['input_lra'], j['input_thresh'], j['target_offset'])
ln = (f"loudnorm=I=-16:TP=-1:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
      f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'segs/pre.mp4', '-af', ln,
                '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2',
                '-movflags', '+faststart', OUT], check=True)
print('done:', OUT)
