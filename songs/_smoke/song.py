"""8-bar neo-soul loop used to smoke-test the pipeline end to end."""
from songwriter.instruments import surge
from songwriter.song import Song


def compose() -> Song:
    s = Song("Smoke Test", bpm=84, key="Eb")
    keys = s.track("keys", "epiano.rhodes")
    bass = s.track("bass", "bass.darkblack")
    drums = s.track("drums", "drums.virtuosity")
    pad = s.track("pad", surge("Pads/MKS-70 Warm Pad"))

    prog = ["Ebmaj9", "Cm9", "Abmaj9", "Bb13"] * 2
    for bar, ch in enumerate(prog):
        b = s.bar(bar)
        keys.chord(ch, b, 3.8, vel=62, octave=3, strum=0.02)
        keys.chord(ch, b + 2.5, 1.4, vel=50, octave=3)
        pad.chord(ch, b, 4, vel=70, octave=4)
        root = ch[:2] if ch[1] in "b#" else ch[0]
        bass.note(f"{root}1", b, 1.5, 92).note(f"{root}2", b + 1.75, 0.25, 70).note(f"{root}1", b + 2.5, 1.2, 86)
        for beat in range(4):
            drums.hit("kick", b + beat, 105) if beat in (0,) else None
            if beat in (1, 3):
                drums.hit("snare", b + beat, 100)
            for eighth in (0, 0.5):
                drums.hit("hh_closed", b + beat + eighth, 78 if eighth == 0 else 58)
        drums.hit("kick", b + 2.5, 92)
    keys.humanize(10, 6); bass.humanize(6, 5); drums.humanize(5, 8).swing(0.56)

    s.mix = {
        "tracks": {
            "drums": {"gain": 0, "eq": [("hpf", 35), ("bell", 400, -2, 1.0), ("hshelf", 9000, 1.5)],
                      "comp": {"threshold": -20, "ratio": 3, "attack": 15, "release": 100},
                      "sends": {"room": -14}},
            "bass": {"gain": -1, "eq": [("hpf", 35), ("bell", 250, -2, 1.2)],
                     "comp": {"threshold": -22, "ratio": 4, "attack": 20, "release": 120},
                     "duck": {"by": "drums", "depth": 2}, "mono": True},
            "keys": {"gain": -3, "eq": [("hpf", 120), ("bell", 350, -2.5, 1.0)],
                     "tube": {"drive": 2}, "width": 1.2, "sends": {"plate": -10}},
            "pad": {"gain": -10, "eq": [("hpf", 250), ("lpf", 9000)], "width": 1.5,
                    "duck": {"by": "drums", "depth": 3}, "sends": {"plate": -6}},
        },
        "fx": {"room": {"type": "reverb", "kind": "room", "decay": 0.7, "predelay": 5},
               "plate": {"type": "reverb", "kind": "plate", "decay": 2.0, "predelay": 25}},
        "master": {"glue": {"threshold": -18, "ratio": 2, "attack": 30, "release": 200}, "target_lufs": -14},
    }
    return s
