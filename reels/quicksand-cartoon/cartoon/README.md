# Quicksand 3D cartoon short: build files

Voiceover by the owner (`voice.wav`), picture timed to it. three.js r160 toon world with ink hulls and billboard cartoon cards.

    cd web && npm i && python3 -m http.server 8765 --bind 127.0.0.1 &   # serve the page
    python3 timing.py voice.wav ../script.txt                            # (phrase timing; already in work/phrases.json)
    node render.mjs frames "0-1092"                                     # about 0.85 s/frame on 2 CPUs
    python3 audio.py && python3 mix.py voice.wav work/music.wav work/sfx.wav work/mix.wav
    ./finish.sh "Quicksand"

Music (kick/clap/hat + synth bass and arp at 120.5 bpm, phrase starts on the 8th-note grid) and SFX sit at 50 % of the voice's gated RMS (-6 dB).
