# What-If Reels: house rules and daily run

This repo makes one "What if?" reel a day for the owner's public Instagram, YouTube Shorts and Facebook channels.
Read this file fully before starting a run.

## Hard rules

- **Never publish without the owner's approval.** Each run makes the reel, sends it to the owner, and queues it in Metricool as a draft or a post waiting for approval. A reel goes public only after the owner says yes in the conversation or approves it in Metricool.
- **No unsupported claims.** Check every number and fact with a web search before it goes in the script. Use "about" for estimates, and drop any claim you cannot back up. Note the sources in `reels/<slug>/sources.md`.
- **Mainstream-safe.** No gore, no real people or celebrities, no current news, no copyrighted characters or brands. Danger stays suspenseful, never graphic.
- **Correct scale.** When the topic changes sizes, draw every shot to true scale against real-size props (`with World(ctx, k)` in centimetres). Never show a shrunken person at full size.

## Style the owner likes

The owner preferred the first "everyone shrank" reel (`reels/everyone-shrank`) over a stricter, faster rework. Match it:

- **Length:** 45 to 55 seconds.
- **Hook:** the first 10 seconds must be the most dramatic part, with no slow intro. Open on the event itself.
- **Jokes:** at least 3 light jokes, some with an Indian flavour. Examples that landed: "honk like you're stuck in Delhi traffic", "spin like a Bollywood hero, minus the slow-mo", "a shoebox is a 1BHK in Mumbai. Still overpriced."
- **Characters:** big, expressive characters on screen (faces readable), not tiny figures lost in the frame.
- **Voice:** Kokoro `am_michael` at speed **0.9**, split into short phrases. Give each phrase a style from `reelkit/voice.py` so the pitch rises and falls. Vary the styles: dramatic for the hook, question for setups, deadpan or funny for punchlines.
- **Script:** short, visual sentences. No filler and no repeated phrases.
- **Pacing:** a meaningful new visual every 1 to 2 seconds.
- **Look:** bright blue, pink, yellow and white on a dark blue-purple background. Big word-by-word captions (built in). Title chip at the top: "WHAT IF ...?" in capitals.
- **Ending:** a question that invites comments, or "Follow for more what-ifs!".

## Daily run procedure

1. **Pick the topic.** Open the ideas Sheet, https://claude.ai/artifact/VJmEgxpFpMsakpwdZubwN7, with the Claude Docs tools (Sheets topics). Take the highest-ranked idea in the "Top 15" tab whose Status in "All 50 Ideas" is blank. When the Top 15 are used up, take the highest viral score left. Set its Status to "In progress".
2. **Research.** Verify every fact the reel will state, and write the sources to `reels/<slug>/sources.md`.
3. **Write `reels/<slug>/script.json`.** Copy the shape of `reels/everyone-shrank/script.json`: lines (one per scene, phrases with style, pause, speed 0.9, caption), `title_chip`, `post.instagram`, `post.facebook`, `post.youtube_title`, `post.youtube_description` and `post.youtube_tags`, following the caption rules in Metricool details.
4. **Write `reels/<slug>/scenes.py`.** Use `reelkit.lib`, and reuse props and characters before drawing new ones. Sync visual beats to word times with `wt(scene, "word")`. Add `sfx(A)` for sound effects.
5. **Preview.** Run `python3 -m reelkit.make reels/<slug> --stills ...` with about 10 times spread over the reel. Look at `build/contact_sheet.png` and fix overlaps, off-screen elements, unreadable text and wrong scale. Repeat until clean.
6. **Build.** Run `python3 -m reelkit.make reels/<slug>`. Check that the length is 45 to 55 seconds. If it is longer, cut a line instead of speeding up the voice.
7. **Commit.** Commit `reels/<slug>/` (script, scenes, sources and the final `out/<slug>.mp4`) to `main`.
8. **Queue for approval.** Send the video to the owner. Put it into Metricool as three drafts (Instagram Reel, Facebook Reel, YouTube Short) at the next day's best times, with network-specific captions (see Metricool details). Set the Sheet Status to "Awaiting approval".
9. **After approval.** Schedule or publish it in Metricool and set the Sheet Status to "Posted" with the date. If the owner asks for changes, make them, rebuild and send the video again.

## Library notes

- Screen is 1080x1920 at 30 fps. Captions sit at y=1400 and the title chip at y≈300. Keep visuals between y=440 and y=1250, and keep text clear of the bottom 320 px, where the app's buttons and captions cover it.
- `popchip(ctx, text, x, y, t_since_start, bg, fg, size)` shows the small labels. `stamp(...)` shows a slammed red stamp.
- `person(ctx, x, feet_y, height, shirt, expr, arms, t)`: expr is smile, shock, worry or cheeks. arms is down, up, wave, run or cheeks.
- In `World(ctx, k)`, 17 cm is a person shrunk to 1/10. Props use typical real sizes: door 200 cm with the handle at 100 cm, counter 90 cm, chair seat 45 cm, phone 15 cm, stair step 17 cm.

## Metricool details

- Brand "kaamkagyann", blogId `8189079`, timezone Asia/Calcutta. Instagram, Facebook Page and YouTube are connected.
- Media must be a public URL. After pushing, use `https://raw.githubusercontent.com/kanhaa21/whatif-reels/main/reels/<slug>/out/<slug>.mp4`. Metricool copies the file to its own storage.
- Queue each reel as **three separate drafts**, one per network, with `createScheduledPost` and `"draft": true`, for the **next day**. Each draft goes at that network's best hour from `getBestTimeToPostByNetwork` (brand 8189079, Asia/Calcutta) and must not clash with a post already scheduled that day; check `getScheduledPosts`. Typical peaks: Instagram about 10:00 (second peak 18:00), Facebook about 12:00, YouTube about 16:00. A draft never publishes by itself. The owner approves by opening the `plannerUrl` and scheduling it. If the owner approves in the conversation instead, call `updateScheduledPost` to set `draft` to false.
- Providers: instagram `{"type": "REEL", "showReelOnFeed": true, "isAiGenerated": true}`; facebook `{"type": "REEL", "title": <short title>}`; youtube `{"title": <youtube_title>, "type": "short", "privacy": "public", "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": false, "tags": [...]}`.
- Write the text separately for each network:
  - **Instagram:** line 1 is the hook, the scariest or funniest fact in under 15 words, with one emoji. Then 1 or 2 lines of payoff that use the reel's best joke. Then an engagement question that is easy to answer ("Comment YES or NO", "How many did you know? Comment the number"). Then "Follow @kaamkagyann for a new what-if every day." Then **exactly 5 hashtags**, the maximum Instagram allows: #WhatIf plus 4 specific to the topic (for example #RoadSafety #DrivingTips, #ScienceFacts #Physics). Never use generic tags like #viral or #reels.
  - **Facebook:** the same hook and question, with a "share this with..." line, and 3 hashtags.
  - **YouTube:** the title is under 70 characters: a curiosity hook, one emoji and `#shorts`. The description is a 2 to 3 sentence summary with the key facts (good for search), then the question, "Subscribe for a new what-if every day.", then `#shorts` plus 2 topic hashtags. Add 6 to 8 tags, including the topic phrases and "kaamkagyann".
  - Every claim in a caption must come from the reel's verified facts. No "most people..." claims without a source.
