# School After Dark Part 2: build

    python3 voice_build.py                         # voice.wav; chunks placed at work/phrases_lock.json times
                                                   # w/we chunks use whisper2.py (tense whisper matched to work/ref_tensed_whisper.wav)
    cp work/phrases.json web/phrases.json
    cat web/base_part1.js web/story.js > web/main.js
    cd web && npm i three@0.160.0 && python3 -m http.server 8767 --bind 127.0.0.1 &
    node render.mjs frames "0-1548"                # 30 fps JPEG frames (about 1 s/frame)
    python3 audio.py && python3 mix.py voice.wav work/music.wav work/sfx.wav work/mix.wav
    mkdir -p out && bash finish.sh "school after dark part2" && mv out/school-after-dark-part2.mp4 ../out/

`web/base_part1.js` is Part 1's world (school, classroom, hallway, cards, torch) unchanged; `web/story.js` is this part.
Captions are burned in by the page (red typewriter; the mimic voices in white italics).
