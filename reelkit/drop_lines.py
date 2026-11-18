"""Remove whole voice lines (and their scenes) from a reel to shorten it.

    python3 -m reelkit.drop_lines reels/<slug> 1 3

Deletes those lines from script.json and their functions from SCENES, and renumbers
wt(N, ...), A.W(N, ...), A.S(N) and MUSIC["beat_from_scene"] in scenes.py.
Any reference to a dropped line is reported; fix those by hand, then build with --revoice."""
import json, re, sys


def main():
    d = sys.argv[1].rstrip("/")
    drop = sorted({int(x) for x in sys.argv[2:]})
    sp = f"{d}/script.json"; cp = f"{d}/scenes.py"
    script = json.load(open(sp))
    n = len(script["lines"])
    keep = [i for i in range(n) if i not in drop]
    new_idx = {old: new for new, old in enumerate(keep)}
    script["lines"] = [script["lines"][i] for i in keep]
    json.dump(script, open(sp, "w"), indent=1, ensure_ascii=False)

    src = open(cp).read()
    m = re.search(r"^SCENES\s*=\s*\[([^\]]*)\]", src, re.M)
    names = [x.strip() for x in m.group(1).split(",") if x.strip()]
    src = src[:m.start()] + "SCENES = [" + ", ".join(names[i] for i in keep) + "]" + src[m.end():]
    bad = []

    def renum(mm):
        pre, num = mm.group(1), int(mm.group(2))
        if num in drop:
            bad.append(mm.group(0)); return mm.group(0)
        return f"{pre}{new_idx[num]}"
    src = re.sub(r"(\bwt\(|\bA\.W\(|\bA\.S\()(\d+)", renum, src)
    src = re.sub(r'("beat_from_scene":\s*)(\d+)', lambda mm: f"{mm.group(1)}{new_idx.get(int(mm.group(2)), 0)}", src)
    open(cp, "w").write(src)
    print(f"kept lines {keep} -> {len(keep)} scenes")
    if bad:
        print("references to dropped lines (fix by hand):", sorted(set(bad)))


if __name__ == "__main__":
    main()
