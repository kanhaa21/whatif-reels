# What-If Reels: house rules and daily run

This repo makes one "What if?" reel a day for the owner's public Instagram, YouTube Shorts and Facebook channels.
Read this file fully before starting a run.

## Hard rules

- **Standing approval to publish (owner, 18 Nov 2026).** The owner asked each daily run to make the reel and schedule it to publish by itself, without waiting for approval. Each run schedules the three posts (not drafts), then sends the owner the video, the times and the Metricool links so they can still change or cancel a post before it goes out. Only publish a reel that built cleanly and passed every check below; if anything fails, stop and tell the owner instead of posting.
- **No unsupported claims.** Check every number and fact with a web search before it goes in the script. Use "about" for estimates, and drop any claim you cannot back up. Note the sources in `reels/<slug>/sources.md`.
- **Mainstream-safe.** No gore, no real people or celebrities, no current news, no copyrighted characters or brands. Danger stays suspenseful, never graphic.
- **Correct scale.** When the topic changes sizes, draw every shot to true scale against real-size props (`with World(ctx, k)` in centimetres). Never show a shrunken person at full size.

## Card style (owner, 21 Nov 2026): the current house style

The owner did not like the cartoon look of the 21 Nov lift reel and asked for the style of two reference reels they sent (tech explainers). `reels/lift-cable-snaps` (v2) is the template; copy it. This overrides the Look, Voice, Characters and Jokes points in the next section:

- Set `"style": "card"` in script.json and draw with `reelkit/cards.py`. Near-black screen with a soft colour glow, no title chip. Each beat has a small grey kicker line over a bold white headline with one accent word (`headline`). Centre content is clean neon-bordered UI cards (`card`, `numcard` "01 02 03" step cards, `pill` tags, slammed `stamp`), simple icons and diagrams, not cartoon people. Small word-by-word captions at y=1330 are built in.
- **English only** (owner, 21 Nov 2026), for the voice and all on-screen text. Voice: Kokoro `af_heart` (female), `"lang": "en-us"`, speed about 0.95. Mix high styles (question, excited, build) with low ones (low, dramatic, deadpan) for clear rise and fall.
- **Voice on the beat** (owner, 21 Nov 2026): set `"timing": {"lead": 0.15, "gap": 0.3, "tail": 1.0, "precut": 0.1, "grid": 0.3}`. With `grid`, every phrase and line starts on an 8th-note grid and a light kick/drum loop (100 bpm) plays on the same grid from frame 0. Keep phrase pauses small (about 0.05 to 0.1); the grid adds the gaps.
- Keep it simple: one idea per beat, about 35 seconds, a new card or tag every 1 to 2 seconds. One light joke is enough.

## Style the owner likes (before 21 Nov 2026)

The owner's favourite is the brake-failure reel (`reels/brake-failure`, "brakes fail at 100 km/h"): engaging, clear and explanatory, with thriller and suspense, one step at a time. They also liked the first "everyone shrank" reel (`reels/everyone-shrank`). Make every reel like those. One-off experiments (`reels/shadow-part1`, `reels/wrong-doors`) are not the house style; the owner asked to drop them.

- **Length:** 30 to 40 seconds (changed from 45 to 55 on 18 Nov 2026 for watch time; see Engagement rules).
- **Hook:** the first 10 seconds must be the most dramatic part, with no slow intro. Open on the event itself.
- **Jokes:** at least 3 light jokes, some with an Indian flavour. Examples that landed: "honk like you're stuck in Delhi traffic", "spin like a Bollywood hero, minus the slow-mo", "a shoebox is a 1BHK in Mumbai. Still overpriced."
- **Characters:** big, expressive characters on screen (faces readable), not tiny figures lost in the frame.
- **Voice:** Kokoro `am_michael` at speed **0.9**, split into short phrases. Give each phrase a style from `reelkit/voice.py` so the pitch rises and falls. Vary the styles: dramatic for the hook, question for setups, deadpan or funny for punchlines.
- **Script:** short, visual sentences. No filler and no repeated phrases.
- **Pacing:** a meaningful new visual every 1 to 2 seconds.
- **Look:** bright blue, pink, yellow and white on a dark blue-purple background. Big word-by-word captions (built in). Title chip at the top: "WHAT IF ...?" in capitals.
- **Ending:** a question that invites comments, or "Follow for more what-ifs!".

## Engagement rules (added 18 Nov 2026)

The first four reels each got only a few views. Instagram's head says the top ranking signals are **watch time, likes per reach and sends per reach**, and sends count most for reaching people who don't follow you. Every reel must be built for those:

- **Watch time.** 30 to 40 seconds and at most 8 voice lines. No scene longer than about 5 seconds. Cut any line that only sets the mood.
- **First frame.** Set `"hook": {"text": ["LINE 1", "LINE 2"], "until": 2.3}` in script.json. It is two short, alarming lines of 4 words or fewer each, shown huge from frame 0, because muted viewers decide in about a second. The first spoken word starts within 0.3 seconds. Never open on a slow scene-setter ("Tonight...").
- **Open a loop.** In the first 5 seconds, promise the payoff ("the last step is the one that saves you"). Deliver it at the end.
- **Sends.** Set `"end_cta": "SEND THIS TO <a specific person>"` (for example "SOMEONE WHO DRIVES", "YOUR TRAVEL BUDDY"). The last voice line also asks viewers to send it or tag someone specific.
- **Comments.** End on a question with a one-word answer (YES/NO, a number). Put the same question in Instagram's `firstCommentText`.
- **Spacing.** At most one reel per platform in any 5-hour window, ideally one a day per platform.
- **Learn from the numbers.** Each run starts by pulling the previous reels' stats with `getAnalyticsDataByMetrics`: Instagram reels IGRE23 views, IGRE24 average watch time, IGRE27 retention, IGRE30 skip rate, IGRE21 shares, IGRE12 saves; YouTube YTVP06 views and YTVP08 average view duration; Facebook FBRE10 views. Add 2 or 3 bullet points of what worked to `insights.md`, and apply them to the new reel. Metricool's stats can lag by about a day.

## Daily run procedure

0. **Review stats.** Follow "Learn from the numbers" in Engagement rules.
1. **Pick the topic.** Open the ideas Sheet, https://claude.ai/artifact/VJmEgxpFpMsakpwdZubwN7, with the Claude Docs tools (Sheets topics). Take the highest-ranked idea in the "Top 15" tab whose Status in "All 50 Ideas" is blank. When the Top 15 are used up, take the highest viral score left. Set its Status to "In progress".
   **Owner's queue (set 18 Nov 2026), used before the rule above:** one reel a day. The reel for Fri 20 Nov is "What if you became invisible for a day?"; the reel for Sat 21 Nov is "What if your lift cable snapped on the 40th floor?". Skip any of these whose Status is already filled in. After both are done, go to the next queue.
   **Owner's everyday-emergencies queue (set 20 Nov 2026), used next, one topic a day in this order.** Each comes with the owner's hook line; use it (or a close variant) as the first spoken line and show the situation in the first second:
   1. Phone catches fire while charging: "Your phone starts smoking beside your pillow." (made on 21 Nov 2026 as `reels/phone-fire-charging` in card style; sent to the owner for approval, not scheduled)
   2. Trapped in a lift: "The lift stopped, and your phone has no signal."
   3. Car breaks down in the middle of nowhere: "No network. No lights. 20 kilometres from help."
   4. Lost in a parking garage: "The same car has passed you three times."
   5. Gas leak at night: "You smell gas, but the kitchen light is already on."
   6. Tyre bursts at high speed: "The steering wheel suddenly starts shaking."
   These topics are not in the ideas Sheet, so skip the Sheet steps for them and track them here instead (mark each as made, with its slug). For these six, the owner asked (20 Nov 2026) for: about 35 seconds; a female voice; the essential safe action inside the same video (never held back for a Part 2); a visual change every 1 to 2 seconds; escalation, one surprising detail and a satisfying payoff; easy to follow with the sound off. **Review first:** for these six, do not schedule. Send the owner the video and wait for their approval before scheduling (this overrides the standing approval for these topics only).
2. **Research.** Verify every fact the reel will state, and write the sources to `reels/<slug>/sources.md`.
3. **Write `reels/<slug>/script.json`.** Copy the shape of `reels/everyone-shrank/script.json`: lines (one per scene, phrases with style, pause, speed 0.9, caption), `title_chip`, `post.instagram`, `post.facebook`, `post.youtube_title`, `post.youtube_description` and `post.youtube_tags`, following the caption rules in Metricool details.
4. **Write `reels/<slug>/scenes.py`.** Use `reelkit.lib`, and reuse props and characters before drawing new ones. Sync visual beats to word times with `wt(scene, "word")`. Add `sfx(A)` for sound effects.
5. **Preview.** Run `python3 -m reelkit.make reels/<slug> --stills ...` with about 10 times spread over the reel. Look at `build/contact_sheet.png` and fix overlaps, off-screen elements, unreadable text and wrong scale. Repeat until clean.
6. **Build.** Run `python3 -m reelkit.make reels/<slug>`. Check that the length is 30 to 40 seconds. If it is longer, cut whole lines with `python3 -m reelkit.drop_lines reels/<slug> <line numbers>` (then fix the references it reports and rebuild with `--revoice`) instead of speeding up the voice.
7. **Commit.** Commit `reels/<slug>/` (script, scenes, sources and the final `out/<slug>.mp4`) to `main`.
8. **Schedule it.** Put it into Metricool as three scheduled posts (Instagram Reel, Facebook Reel, YouTube Short) with `"draft": false`, at the next day's best times, with network-specific captions (see Metricool details). Set the Sheet Status to "Posted" and "Posted on" to the publish date.
9. **Tell the owner.** Send the video with SendUserFile and one short message with the topic, the three times and the three `plannerUrl`s, so they can change or cancel before it goes out. If the owner asks for changes, make them, rebuild, push and update the posts' media.

## Library notes

- Screen is 1080x1920 at 30 fps. Captions sit at y=1400 and the title chip at y≈300. Keep visuals between y=440 and y=1250, and keep text clear of the bottom 320 px, where the app's buttons and captions cover it.
- `popchip(ctx, text, x, y, t_since_start, bg, fg, size)` shows the small labels. `stamp(...)` shows a slammed red stamp.
- `person(ctx, x, feet_y, height, shirt, expr, arms, t)`: expr is smile, shock, worry or cheeks. arms is down, up, wave, run or cheeks.
- In `World(ctx, k)`, 17 cm is a person shrunk to 1/10. Props use typical real sizes: door 200 cm with the handle at 100 cm, counter 90 cm, chair seat 45 cm, phone 15 cm, stair step 17 cm.

## Metricool details

- Brand "kaamkagyann", blogId `8189079`, timezone Asia/Calcutta. Instagram, Facebook Page and YouTube are connected.
- Media must be a public URL. After pushing, use `https://raw.githubusercontent.com/kanhaa21/whatif-reels/main/reels/<slug>/out/<slug>.mp4`. Metricool copies the file to its own storage.
- Schedule each reel as **three separate posts**, one per network, with `createScheduledPost` and `"draft": false`, for the **next day**. Each post goes at that network's best hour from `getBestTimeToPostByNetwork` (brand 8189079, Asia/Calcutta) and must not clash with a post already scheduled that day; check `getScheduledPosts`. Typical peaks: Instagram about 10:00 (second peak 18:00), Facebook about 12:00, YouTube about 16:00. Keep the Spacing rule (one reel per platform in any 5-hour window): if the best hour is taken, use the next-best free hour. Scheduled posts publish automatically; the owner can still edit or cancel them from the `plannerUrl`.
- Providers: instagram `{"type": "REEL", "showReelOnFeed": true, "isAiGenerated": true}`; facebook `{"type": "REEL", "title": <short title>}`; youtube `{"title": <youtube_title>, "type": "short", "privacy": "public", "category": "EDUCATION", "madeForKids": false, "isAiGeneratedContent": false, "tags": [...]}`.
- Write the text separately for each network:
  - **Instagram:** line 1 is the hook, the scariest or funniest fact in under 15 words, with one emoji. Then 1 or 2 lines of payoff that use the reel's best joke. Then an engagement question that is easy to answer ("Comment YES or NO", "How many did you know? Comment the number"). Then "Follow @kaamkagyann for a new what-if every day." Then **exactly 5 hashtags**, the maximum Instagram allows: #WhatIf plus 4 specific to the topic (for example #RoadSafety #DrivingTips, #ScienceFacts #Physics). Never use generic tags like #viral or #reels.
  - **Facebook:** the same hook and question, with a "share this with..." line, and 3 hashtags.
  - **YouTube:** the title is under 70 characters: a curiosity hook, one emoji and `#shorts`. The description is a 2 to 3 sentence summary with the key facts (good for search), then the question, "Subscribe for a new what-if every day.", then `#shorts` plus 2 topic hashtags. Add 6 to 8 tags, including the topic phrases and "kaamkagyann".
  - Every claim in a caption must come from the reel's verified facts. No "most people..." claims without a source.
