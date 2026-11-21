import subprocess, sys, os, textwrap

CHK = r"C:\Users\Administrator\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.user_skills\minimax-h3-video-prompts\scripts\check_h3_prompt.py"
TMP = os.path.join(os.path.dirname(CHK), "_test")
os.makedirs(TMP, exist_ok=True)

good_i2va = textwrap.dedent("""\
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Cinematic, live-action, the young man in dark official robes shown in <Picture 1> remains before the city gate, preserving his face, robe pattern, and hat shape. The camera pushes in with small amplitude at slow speed as he lifts his gaze. The guard (S1) shouts in a rough voice, <d>[Chinese] 站住！</d> while his spear tip stays at the man's throat.

overall_soundscape: Cold morning wind sweeps through the gate arch. Iron spear shafts scrape against leather armor, followed by a single heavy swallow.

non_diegetic_music: N/A
""")

good_ref = textwrap.dedent("""\
subject_definitions:
<Subject 1> is the young scholar in <Picture 1>, with a thin build, a blue-grey linen robe, and a topknot.
<Subject 2> is the inn room in <Picture 2>, with a square wooden table, two benches, a candle stand, and a gray plaster wall.

summary:
[reference generation] The target video shows <Subject 1> rehearsing an official tone inside <Subject 2> before a woman in red knocks.

retention_analysis:
<Subject 1> (appears in [Shot 1], [Shot 2]): fully_preserved - his face, robe, and hair are retained.
<Subject 2> (appears in [Shot 1]): partially_preserved - the table and candle are retained while camera angle changes.

detailed_description:
Cinematic, live-action, warm candlelight with soft falloff.
[Shot 1] A medium shot establishes <Subject 2>, the inn room, and <Subject 1>, who stands before a small bronze mirror and straightens his hat. The camera holds a static shot as he opens his mouth without sound.
[Shot 2] At 00:03.000, the shot cuts to a close-up of his throat as the word finally comes out, thin and unsteady.

overall_soundscape:
A candle wick crackles softly over a quiet room tone, with fabric shifting as he adjusts his sleeves.

non_diegetic_music:
Sparse low strings at a slow tempo, fading before the cut.
""")

bad_i2va = textwrap.dedent("""\
integrated_multimodal_description: [Shot 1] 电影感写实，人物站在城门前，手持一支长枪，dolly in 到他的脸。他说“站住”。
overall_soundscape: 风声，他在说台词，背景音乐紧张。
non_diegetic_music: 紧张的配乐
""")

DRAFT = r"D:\AAA\text\假钦差\短剧\_h3chk\ep02_s01.txt"

cases = [
    ("good_i2va", "single-image", "good_i2va.txt", good_i2va, 5),
    ("good_ref", "multimodal", "good_ref.txt", good_ref, 5),
    ("bad_i2va", "single-image", "bad_i2va.txt", bad_i2va, 5),
    ("cn_draft_ep02_s01", "single-image", None, None, 5),
]

for name, mode, fn, content, dur in cases:
    if fn:
        p = os.path.join(TMP, fn)
        open(p, "w", encoding="utf-8").write(content)
    else:
        p = DRAFT
    r = subprocess.run([sys.executable, CHK, p, "--mode", mode, "--duration", str(dur)],
                       capture_output=True, text=True)
    print(f"\n##### {name} (exit {r.returncode})")
    print(r.stdout.strip())
