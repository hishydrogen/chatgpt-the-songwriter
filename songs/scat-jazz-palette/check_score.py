"""Pre-render checks for written harmony, performance, MIDI channels and phonemes."""
import importlib.util
import json
from pathlib import Path

from songwriter import config, instruments, voice

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("palette_score", HERE / "song.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song = score.compose()

# Every scat pitch is a deliberately chosen chord tone or extension. Passing bass
# approaches (Db->C, Ab->A and F#->G) and anticipations are written separately.
allowed = {"Fmaj9": {0,4,5,7,9}, "F6/9": {0,2,5,7,9},
           "D7b9": {0,2,3,6,9}, "Gm9": {2,5,7,9,10},
           "C13": {0,2,4,7,9,10}, "Am7": {0,4,7,9}, "Bbm6": {1,5,7,10}}
for bar, line in enumerate(score.HOOK):
    for pos,pitch,length,syllable in line:
        _,symbol,_,_ = score.chord_at(bar*4+pos)
        assert score.N(pitch)%12 in allowed[symbol], (bar,pos,pitch,symbol)

for t in song.tracks.values():
    inst = instruments.get_instrument(t.instrument)
    assert inst.available, inst.id
    assert all(0<=n.pitch<=127 and n.dur>0 and n.start>=0 for n in t.notes), t.name
    assert len({n.vel for n in t.notes}) > 1 if len(t.notes)>10 else True
    if inst.engine == "voice":
        ns = [voice.VNote(song.seconds(n.start),song.seconds(n.start+n.dur),
                         n.pitch,n.lyric,n.vel,n.x) for n in t.notes]
        pieces = voice._plan(ns,voice.bank(inst.path),{**voice.DEFAULTS,**t.opts},light=True)
        print(t.name, len(ns), "notes;",len({p.oto.alias for p in pieces}),"sample aliases")
        assert min(n.midi for n in ns)>=60 and max(n.midi for n in ns)<=70

mf = song.full_midi()
lyric_count = 0
for mt,t in zip(mf.tracks[1:],song.tracks.values()):
    assert all(m.channel==t.channel for m in mt if hasattr(m,"channel")),t.name
    lyric_count += sum(m.type=="lyrics" for m in mt)
assert lyric_count == sum(bool(n.lyric) for t in song.tracks.values() for n in t.notes)

# Compare every singer's note/duration/dynamic/performance event against the same take.
vs = [song.tracks[label] for label,_ in score.VOICES]
signatures = [[(round(n.start-t.notes[0].start,7),n.pitch,round(n.dur,7),n.vel,n.lyric,n.x)
               for n in t.notes] for t in vs]
assert all(s==signatures[0] for s in signatures[1:]),"candidate performances differ"

result = {"status":"passed","bpm":score.BPM,"swing":score.SWING,
          "tracks":len(song.tracks),"notes":sum(len(t.notes) for t in song.tracks.values()),
          "scat_notes_per_voice":len(vs[0].notes),"midi_lyrics":lyric_count,
          "sections":[{**s,"start_s":round(song.seconds(s['beat']),2),
                       "end_s":round(song.seconds(s['beat']+s['bars']*4),2)}
                      for s in song.palette_sections]}
(HERE/"score-check.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
