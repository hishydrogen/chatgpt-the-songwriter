"""Verify both newly added harmony performances, including the key change."""
import importlib.util
import json
from pathlib import Path

import numpy as np
import pyworld as pw
from scipy import signal
import soundfile as sf

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("swing_milk_harmonies",HERE/"song.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song=score.compose()

def estimate(x,sr):
    mono=signal.resample_poly(x,16000,sr) if sr!=16000 else x
    return pw.harvest(np.ascontiguousarray(mono,dtype=np.float64),16000,
                      f0_floor=170,f0_ceil=750,frame_period=10)

tt=np.arange(32000)/16000
f0,_=estimate(sum(.1/k*np.sin(2*np.pi*440*k*tt) for k in (1,2,3)),16000)
assert abs(np.median(f0[f0>0])-440)<3
results={}
for label in ("Milk harmony left","Milk harmony right"):
    track=song.tracks[label]
    errors=[]
    for sec in song.form_sections:
        notes=[n for n in track.notes if sec["beat"]<=n.start<sec["beat"]+sec["bars"]*4]
        if not notes:
            continue
        start=song.seconds(sec["beat"])
        end=song.seconds(sec["beat"]+sec["bars"]*4)
        with sf.SoundFile(HERE/"out/stems"/(label+".wav")) as f:
            sr=f.samplerate
            f.seek(round(start*sr))
            x=f.read(round((end-start+.3)*sr)).mean(axis=1)
        f0,t=estimate(x,sr)
        voiced=f0>0
        midi=np.full_like(f0,np.nan)
        midi[voiced]=69+12*np.log2(f0[voiced]/440)
        for n in notes:
            a=song.seconds(n.start)-start
            b=song.seconds(n.start+n.dur)-start
            window=(t>=a+.065)&(t<=b-.03)&voiced
            if window.sum()>=3:
                errors.append({"section":sec["name"],"beat":round(n.start,3),"pitch":n.pitch,
                               "error_cents":round(float(np.median(midi[window]-n.pitch)*100),1)})
    absolute=np.abs([n["error_cents"] for n in errors])
    assert len(errors)>=len(track.notes)*.9
    assert np.median(absolute)<35 and np.max(absolute)<80,(label,errors)
    results[label]={"written_notes":len(track.notes),"measured_notes":len(errors),
                    "median_absolute_error_cents":round(float(np.median(absolute)),1),
                    "maximum_absolute_error_cents":round(float(np.max(absolute)),1)}
    print(label,results[label],flush=True)
(HERE/"out/harmony-check.json").write_text(json.dumps({"status":"passed","harmonies":results},indent=2))
