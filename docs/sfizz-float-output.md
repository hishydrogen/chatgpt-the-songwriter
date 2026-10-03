# Preserve precision and headroom before mixing

The pinned upstream `sfizz_render` converts its internal float buffer to 16-bit PCM
before writing a temporary WAV. Quiet instruments acquire quantization noise before
stem normalization, and a sum above full scale clips before the mixer can lower it.
Writing the cached stem as FLOAT afterwards cannot recover that data.

`scripts/sfizz-float-output.patch` writes the interleaved float buffer directly as
32-bit IEEE float WAV, including the release tail. `scripts/setup.sh` detects and
rebuilds older renderers. The Python renderer rejects integer output and versions
its SFZ cache signatures so existing integer-rendered stems refresh automatically.
Final delivery remains 24-bit WAV and MP3/ALAC. Original sample resolution is unchanged.

After building and installing the patched native renderer, activate the environment
and run:

```bash
python scripts/check_sfizz_float.py
python songs/low-tide-groove/build.py
```

The first command exercises the actual native renderer through the Python pipeline
with sixteen layers of a synthetic sine. Its float peak is 6.786323; the original
16-bit writer clips this fixture at full scale. Float values also retain precision
below the 16-bit quantization grid. A value above 1 in an internal float signal is
valid headroom; final delivery must still stay below full scale.

The groove build validates non-silent music, raw stems, current MIDI exports,
WAV/decoded-MP3 peaks, comparison loudness, dynamics and mono compatibility. The
renderer's precision change addresses an earlier pipeline stage than the guitar
amp's intentional distortion; the groove also reduces amp input and drive because
the user requested a smoother sound.
