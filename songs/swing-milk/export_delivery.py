"""Package the rough mix's score, section takes, credits and scat performance."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import zipfile

import mido

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("swing_milk_export",HERE/"song.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song=score.compose()
out=HERE/"out"
sections=[]
lyrics=[]
lead=song.tracks[score.VOICE_LABEL]
for sec in song.form_sections:
    sections.append({**sec,"start_s":round(song.seconds(sec["beat"]),2),
                     "end_s":round(song.seconds(sec["beat"]+sec["bars"]*4),2)})
    lyrics.append("["+sec["name"]+"]")
    for bar in range(sec["bars"]):
        b=sec["beat"]+bar*4
        notes=sorted([n for n in lead.notes if b<=n.start<b+4],key=lambda n:n.start)
        if notes:
            lyrics.append(" ".join(score.groove.palette.SCAT[n.lyric] for n in notes))
        else:
            lyrics.append("(instrumental)" if not any(n.start<b and n.start+n.dur>b for n in lead.notes) else "(hold)")
    lyrics.append("")
(HERE/"LYRICS.txt").write_text("\n".join(lyrics))
(out/"sections.json").write_text(json.dumps(sections,indent=2))
(out/"track-map.json").write_text(json.dumps([
    {"name":t.name,"instrument":t.instrument,"channel_zero_based":t.channel}
    for t in song.tracks.values()],indent=2))
chords=[{**c,"pcs":sorted(c["pcs"]),"start_s":round(song.seconds(c["beat"]),3)} for c in song.chord_timeline]
(out/"chords.json").write_text(json.dumps(chords,indent=2))
for sec in song.form_sections:
    if sec["name"] not in ("verse 1","chorus 1","final chorus"):
        continue
    take=copy.deepcopy(song)
    # Section files use a simple conductor, so the full-song modulation marker
    # cannot extend a 16-bar excerpt to 280 beats.
    take.title="Swing, Milk! - "+sec["name"]
    b0,b1=sec["beat"],sec["beat"]+sec["bars"]*4
    take.markers=[(0,sec["name"])]
    take.length_beats=b1-b0+.4
    for t in take.tracks.values():
        t.notes=[n for n in t.notes if b0<=n.start<b1]
        for n in t.notes:
            n.start-=b0
        initial={}
        for b,cc,v in sorted(t.ccs):
            if b<b0:
                initial[cc]=v
        t.ccs=[(0,cc,v) for cc,v in initial.items()]+[(b-b0,cc,v) for b,cc,v in t.ccs if b0<=b<b1+.4]
        t.bends=[(0,0)]+[(b-b0,v) for b,v in t.bends if b0<=b<b1+.4]
    mf=score.groove.palette.PaletteSong.full_midi(take)
    mf.tracks[0].insert(0,mido.MetaMessage("key_signature",key="G" if sec["transpose"]==2 else "F",time=0))
    mf.save(out/"midi"/(sec["name"].replace(" ","-")+".mid"))
archive=out/"swing-milk-midi.zip"
with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
    for p in sorted((out/"midi").glob("*.mid")):
        z.write(p,"midi/"+p.name.replace(" ","_"))
    for p in (HERE/"README.md",HERE/"CREDITS.md",HERE/"LYRICS.txt",HERE/"score-check.json",
              out/"track-map.json",out/"sections.json",out/"chords.json"):
        z.write(p,p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    print(len([p for p in z.namelist() if p.endswith(".mid")]),"MIDI files verified")
with tempfile.TemporaryDirectory(prefix=".metadata-",dir=out) as td:
    tagged=Path(td)/"master.mp3"
    subprocess.run(["ffmpeg","-v","error","-y","-i",str(out/"master.mp3"),
                    "-map","0:a:0","-c:a","copy","-metadata","title="+score.TITLE,
                    "-metadata","album=Checkpoint 3 - rough mix","-metadata","genre=Jazz",
                    "-metadata","comment=Vocal: Milk (Xepheris), rendered with WORLD. Original composition and arrangement: Codex. Commercial voicebank use requires author approval.",
                    str(tagged)],check=True)
    tagged.replace(out/"master.mp3")
print("sections",len(sections),"length",round(song.seconds(song.end_beat)+4,2),"seconds")
