"""Check full-song musical continuity, bank aliases and exported MIDI semantics."""
import importlib.util
import json
from collections import defaultdict
from pathlib import Path

from songwriter import instruments, voice

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("swing_milk_score",HERE/"song.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song=score.compose()
assert song.end_beat==408 and len(song.tracks)==19
sections=song.form_sections
assert [s["groove"] for s in sections if s["kind"]=="verse"]==["A","A"]
assert all(s["groove"]=="B" for s in sections if s["kind"]=="chorus")
assert all(s["groove"]!="C" for s in sections)

def chord_at(beat):
    return next(c for c in reversed(song.chord_timeline) if c["beat"]<=beat+1e-7)

for e in song.written_events:
    chord=chord_at(e["beat"])
    assert e["pitch"]%12 in chord["pcs"],(e,chord["symbol"])

voice_counts={}
for t in song.tracks.values():
    inst=instruments.get_instrument(t.instrument)
    assert inst.available and t.notes,t.name
    assert all(n.start>=0 and n.dur>0 and 1<=n.vel<=127 for n in t.notes),t.name
    if inst.range:
        assert all(inst.range[0]<=n.pitch<=inst.range[1] for n in t.notes),(t.name,inst.range)
    keys=[(n.pitch,round(n.start,6)) for n in t.notes]
    assert len(keys)==len(set(keys)),(t.name,"duplicate note-ons")
    by_pitch=defaultdict(list)
    for n in t.notes:
        by_pitch[0 if inst.engine=="voice" else n.pitch].append(n)
    for notes in by_pitch.values():
        notes.sort(key=lambda n:n.start)
        assert all(a.start+a.dur<=b.start+1e-6 for a,b in zip(notes,notes[1:])),(t.name,"overlapping same-key retrigger")
    if inst.engine=="voice":
        ns=[voice.VNote(song.seconds(n.start),song.seconds(n.start+n.dur),n.pitch,n.lyric,n.vel,n.x) for n in t.notes]
        pieces=voice._plan(ns,voice.bank(inst.path),{**voice.DEFAULTS,**t.opts},light=True)
        voice_counts[t.name]={"notes":len(ns),"aliases":len({p.oto.alias for p in pieces}),
                              "lowest_midi":min(n.pitch for n in t.notes),"highest_midi":max(n.pitch for n in t.notes)}
        print(t.name,voice_counts[t.name],flush=True)

lead=song.tracks[score.VOICE_LABEL]
for sec in sections:
    notes=[n for n in lead.notes if sec["beat"]<=n.start<sec["beat"]+sec["bars"]*4]
    if sec["kind"] in ("verse","lift","chorus","bridge","tag"):
        # Every sung bar has a phrase or an intentional held vowel.
        for bar in range(sec["bars"]):
            b=sec["beat"]+bar*4
            assert any(n.start<b+4 and n.start+n.dur>b for n in notes),(sec["name"],bar,"silent sung bar")
    if sec["kind"] in ("intro","turn"):
        assert not notes,(sec["name"],"unexpected vocal")

mf=song.full_midi()
assert [m.key for m in mf.tracks[0] if m.type=="key_signature"]==["F","G"]
lyric_count=0
for mt,t in zip(mf.tracks[1:],song.tracks.values()):
    assert all(m.channel==t.channel for m in mt if hasattr(m,"channel")),t.name
    active=defaultdict(int)
    for m in mt:
        assert m.time>=0
        if m.type=="note_on" and m.velocity:
            active[m.note]+=1
        elif m.type=="note_off" or m.type=="note_on" and m.velocity==0:
            active[m.note]-=1
            assert active[m.note]>=0
        lyric_count+=m.type=="lyrics"
    assert not any(active.values()),t.name
assert lyric_count==sum(len(t.notes) for t in song.tracks.values() if t.instrument.startswith("voice."))
channels=[t.channel for t in song.tracks.values() if not t.instrument.startswith("drums.")]
assert len(channels)==len(set(channels)),"conflicting expression/pedal channels"
assert chord_at(312)["transpose"]==2 and chord_at(400)["symbol"]=="G6/9"
result={"status":"passed","title":score.TITLE,"selected_instruments":score.SELECTED,
        "bpm":score.BPM,"swing":score.SWING,"bars":102,"tracks":len(song.tracks),
        "notes":sum(len(t.notes) for t in song.tracks.values()),"midi_lyrics":lyric_count,
        "voices":voice_counts,"sections":[{**s,"start_s":round(song.seconds(s["beat"]),2),
        "end_s":round(song.seconds(s["beat"]+s["bars"]*4),2)} for s in sections]}
(HERE/"score-check.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
