"""Measure rendered singer stems against their MIDI and save an inspectable pitch plot."""
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pyworld as pw
from scipy import signal
import soundfile as sf

from songwriter import config

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("palette_score",HERE/"song.py")
score=importlib.util.module_from_spec(spec); spec.loader.exec_module(score)
song=score.compose()
out=HERE/"out"

def estimate(x,sr):
    if sr!=16000:
        x=signal.resample_poly(x,16000,sr)
    return pw.harvest(np.ascontiguousarray(x,dtype=np.float64),16000,
                      f0_floor=180,f0_ceil=750,frame_period=10)

# Check the measurement pipeline with a known harmonic tone before trusting it.
tt=np.arange(32000)/16000
tone=sum(.1/k*np.sin(2*np.pi*440*k*tt) for k in (1,2,3))
f0,t=estimate(tone,16000)
assert abs(np.median(f0[f0>0])-440)<3,"pitch measurement calibration failed"

fig,axes=plt.subplots(3,1,figsize=(14,8),sharex=True,constrained_layout=True)
results={}
for ax,(label,inst),sec in zip(axes,score.VOICES,song.palette_sections[:3]):
    start=song.seconds(sec['beat']); end=song.seconds(sec['beat']+32)
    with sf.SoundFile(out/"stems"/(label+".wav")) as f:
        sr=f.samplerate; f.seek(round(start*sr)); x=f.read(round((end-start+.3)*sr))
    mono=x.mean(axis=1)
    f0,t=estimate(mono,sr)
    midi=np.full_like(f0,np.nan); voiced=f0>0
    midi[voiced]=69+12*np.log2(f0[voiced]/440)
    ax.plot(t,midi,color="#2354b0",lw=.9,label="rendered pitch")
    note_errors=[]
    for n in song.tracks[label].notes:
        a=song.seconds(n.start)-start; b=song.seconds(n.start+n.dur)-start
        ax.plot([a,b],[n.pitch,n.pitch],color="#d69300",lw=2,alpha=.75)
        # Ignore consonants and drawn attack/release bends when assessing tuning.
        window=(t>=a+.065)&(t<=b-.025)&voiced
        if window.sum()>=3:
            error=float(np.median(midi[window]-n.pitch)*100)
            note_errors.append({"beat":round(n.start-sec['beat'],3),"pitch":n.pitch,
                                "syllable":n.lyric,"error_cents":round(error,1)})
    errors=np.array([n['error_cents'] for n in note_errors])
    assert len(errors)>=25,(label,"too few measurable vowels",len(errors))
    median=float(np.median(np.abs(errors)))
    assert median<35,(label,"median intonation error",median)
    # Keep any outliers in the report instead of hiding pitch-estimator failures.
    jumps=np.abs(np.diff(mono))
    local=np.sqrt(signal.convolve(mono**2,np.ones(129)/129,mode='same'))
    candidates=np.flatnonzero((jumps>2.5*local[1:])&(jumps>.035))
    results[label]={"measured_notes":len(errors),"median_absolute_error_cents":round(median,1),
                    "p90_absolute_error_cents":round(float(np.percentile(np.abs(errors),90)),1),
                    "outliers_over_80_cents":[n for n in note_errors if abs(n['error_cents'])>80],
                    "large_sample_jumps":len(candidates),"notes":note_errors}
    ax.set_ylim(58,73); ax.set_ylabel("MIDI pitch"); ax.set_title(label)
    ax.grid(alpha=.2)
    print(label,results[label]['median_absolute_error_cents'],"cents median",flush=True)
axes[-1].set_xlabel("Seconds within the same eight-bar phrase")
fig.suptitle("Scat audition: rendered pitch (blue), written MIDI notes (gold)")
fig.savefig(out/"vocal-pitch.png",dpi=120); plt.close(fig)
(out/"vocal-pitch.json").write_text(json.dumps({"status":"passed","voices":results},indent=2))
