# School After Dark Part 3: build

    python3 voice_build.py                         # voice.wav + work/phrases.json
                                                   # w/we chunks use whisper2.py with Part 2's whisper EQ (work/whisper_eq.npy)
    cp work/phrases.json web/phrases.json
    cat web/base_part1.js web/story.js > web/main.js
    cd web && npm i three@0.160.0 && python3 -m http.server 8768 --bind 127.0.0.1 &
    node render.mjs frames "0-1550"                # 30 fps JPEG frames (about 1 s/frame)
    python3 audio.py && python3 mix.py voice.wav work/music.wav work/sfx.wav work/mix.wav
    mkdir -p out && bash finish.sh "school after dark part3" && mv out/school-after-dark-part3.mp4 ../out/

`web/base_part1.js` is Part 1's world (school, classroom, hallway, cards, torch) unchanged; `web/story.js` is this part.
Captions are burned in by the page (red typewriter; the mimic voices in white italics).
