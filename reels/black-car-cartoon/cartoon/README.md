# "Planning to buy a black car?" 3D cartoon reel: build files

Voice: Kokoro af_heart (female, en-us) generated from `lines.json` with reelkit, every phrase and line snapped to a 0.3 s grid
(8th notes at 100 bpm); `web/timeline.json` holds the word timings used for the burned-in captions.
Same three.js toon engine as `reels/quicksand-cartoon/cartoon`.

    cd web && npm i three@0.160.0 && python3 -m http.server 8766 --bind 127.0.0.1 &
    node render.mjs frames "0-1082"
    python3 audio.py && python3 mix.py voice.wav work/music.wav work/sfx.wav work/mix.wav
    ./finish.sh "Black Car"

Music (kick/clap/hat, synth bass and arp on the same 100 bpm grid, drops out for the punchline) and SFX at 50 % of the voice's gated RMS.
