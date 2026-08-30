"""Print non-health bookmarks for the signal/noise pass."""
import json, sys
recs = json.load(open("data/classified.json"))
pool = [(i, r) for i, r in enumerate(recs) if r["top"] not in ("H", "U")]
if sys.argv[1] == "count":
    import collections
    print(len(pool), "to judge |", collections.Counter(r["top"] for _, r in pool))
else:
    start, n = int(sys.argv[2]), int(sys.argv[3])
    for i, r in pool[start:start + n]:
        print(f"{i}|{r['sub']}|{' '.join(r['text'].split())[:185]}")
