"""Measure the rough mix and every sung section against its actual MIDI targets."""
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

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("swing_milk_audio",HERE/"song.py")
score=importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)
song=score.compose()
out=HERE/"out"
report=json.loads((out/"report.json").read_text())
master=report["master"]
assert abs(master["integrated_lufs"]+14)<=.2 and master["true_peak_dbtp"]<=-.95,master
assert master["plr_db"]>=12 and master["stereo_correlation"]>=.3,master
assert not report["warnings"],report["warnings"]
balances=[]
for sec in report["sections"]:
    if sec["label"] in ("intro","turnaround","scat and tenor trading"):
        continue
    lv=sec["tracks"]
    assert score.VOICE_LABEL in lv,(sec["label"],"missing vocal")
    band=[(v,n) for n,v in lv.items() if not n.startswith(("Milk harmony","fx:","bus:")) and n!=score.VOICE_LABEL]
    band_level,band_name=max(band)
    margin=round(lv[score.VOICE_LABEL]-band_level,1)
    assert margin>=3.5,(sec["label"],"buried lead",margin)
    assert margin<=9,(sec["label"],"lead too far in front",margin)
    balances.append({"section":sec["label"],"lead_lufs":lv[score.VOICE_LABEL],
                     "loudest_instrument":band_name,"loudest_instrument_lufs":band_level,
                     "lead_margin_db":margin})

def estimate(x,sr):
    x=signal.resample_poly(x,16000,sr) if sr!=16000 else x
    return pw.harvest(np.ascontiguousarray(x,dtype=np.float64),16000,
                      f0_floor=170,f0_ceil=750,frame_period=10)

tt=np.arange(32000)/16000
f0,_=estimate(sum(.1/k*np.sin(2*np.pi*440*k*tt) for k in (1,2,3)),16000)
assert abs(np.median(f0[f0>0])-440)<3,"pitch detector calibration failed"
vocal_sections=[s for s in song.form_sections if s["kind"] not in ("intro","turn")]
fig,axes=plt.subplots(len(vocal_sections),1,figsize=(15,2.0*len(vocal_sections)),constrained_layout=True)
results=[]
lead=song.tracks[score.VOICE_LABEL]
for ax,sec in zip(axes,vocal_sections):
    start=song.seconds(sec["beat"])
    end=song.seconds(sec["beat"]+sec["bars"]*4)
    with sf.SoundFile(out/"stems"/(score.VOICE_LABEL+".wav")) as f:
        sr=f.samplerate
        f.seek(round(start*sr))
        x=f.read(round((end-start+.3)*sr))
    mono=x.mean(axis=1)
    f0,t=estimate(mono,sr)
    midi=np.full_like(f0,np.nan)
    voiced=f0>0
    midi[voiced]=69+12*np.log2(f0[voiced]/440)
    ax.plot(t,midi,color="#2354b0",lw=.8)
    errors=[]
    notes=[n for n in lead.notes if sec["beat"]<=n.start<sec["beat"]+sec["bars"]*4]
    for n in notes:
        a=song.seconds(n.start)-start
        b=song.seconds(n.start+n.dur)-start
        ax.plot([a,b],[n.pitch,n.pitch],color="#d69300",lw=2,alpha=.75)
        window=(t>=a+.065)&(t<=b-.03)&voiced
        if window.sum()>=3:
            errors.append({"beat":round(n.start,3),"pitch":n.pitch,
                           "cents":round(float(np.median(midi[window]-n.pitch)*100),1)})
    absolute=np.abs([e["cents"] for e in errors])
    assert len(errors)>=len(notes)*.8,(sec["name"],"too few measurable notes")
    assert float(np.median(absolute))<35,(sec["name"],"intonation")
    outliers=[e for e in errors if abs(e["cents"])>80]
    assert not outliers,(sec["name"],outliers)
    jumps=np.abs(np.diff(mono))
    local=np.sqrt(signal.convolve(mono**2,np.ones(129)/129,mode="same"))
    candidates=np.flatnonzero((jumps>2.5*local[1:])&(jumps>.035))
    jump_times=candidates/sr
    boundaries=[song.seconds(n.start)-start for n in notes]
    # Natural consonants can trip a sample-jump detector. Preserve locations
    # for review and distinguish those from jumps inside sustained vowels.
    unexplained=[round(float(ti),4) for ti in jump_times if not any(-.06<=ti-b<=.09 for b in boundaries)]
    assert not unexplained,(sec["name"],"jumps outside consonant regions",unexplained)
    row={"section":sec["name"],"written_notes":len(notes),"measured_notes":len(errors),
         "median_absolute_error_cents":round(float(np.median(absolute)),1),
         "p90_absolute_error_cents":round(float(np.percentile(absolute,90)),1),
         "outliers_over_80_cents":outliers,"large_sample_jumps":len(candidates),
         "jump_times_within_section_s":[round(float(v),4) for v in jump_times],
         "unexplained_jumps":unexplained}
    results.append(row)
    ax.set_ylim(57,75)
    ax.set_xlim(0,end-start+.3)
    ax.set_ylabel("MIDI pitch")
    ax.set_title(sec["name"])
    ax.grid(alpha=.2)
    print(row,flush=True)
axes[-1].set_xlabel("Seconds within section")
fig.suptitle("Swing, Milk! -- lead pitch: audio (blue), written MIDI (gold)")
fig.savefig(out/"vocal-pitch.png",dpi=100)
plt.close(fig)
result={"status":"passed","master":master,"balances":balances,"lead_pitch":results}
(out/"audio-check.json").write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
