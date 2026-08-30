"""Phase 3: merge hand labels with fallback handling for text-less items."""
import collections, glob, json

REC = "/home/user/blank-app/data/records.json"
TAX = "/home/user/blank-app/data/taxonomy.json"
OUT = "/home/user/blank-app/data/classified.json"

MIN_AUTHOR_ITEMS = 3      # author needs this many labeled bookmarks to vote
AUTHOR_CONCENTRATION = 0.6  # ...and this share in one top-level bucket


def load_labels():
    labels = {}
    for path in sorted(glob.glob("/home/user/blank-app/labels/*.tsv")):
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            idx, sub, tags = line.split("\t")
            labels[int(idx)] = (sub, tags.split(","))
    return labels


def author_profiles(records, labels):
    """Map author -> their labeled sub-buckets, for inferring text-less items."""
    by_author = collections.defaultdict(list)
    for idx, (sub, _) in labels.items():
        by_author[records[idx]["author_id"]].append(sub)
    return by_author


def infer_from_author(record, by_author):
    """Guess a bucket for a text-less item from the rest of that author's shelf."""
    subs = by_author.get(record["author_id"], [])
    if len(subs) < MIN_AUTHOR_ITEMS:
        return None
    top_sub, top_n = collections.Counter(subs).most_common(1)[0]
    top_level, level_n = collections.Counter(s[0] for s in subs).most_common(1)[0]
    if level_n / len(subs) < AUTHOR_CONCENTRATION:
        return None
    # keep the specific sub-bucket only if it also sits in the dominant top level
    sub = top_sub if top_sub[0] == top_level else \
        collections.Counter(s for s in subs if s[0] == top_level).most_common(1)[0][0]
    return sub


def fallback_bucket(record):
    if record["is_article"]:
        return "U1"
    if record["media"]:
        return "U2"
    return "U3"


def build():
    records = json.load(open(REC))
    taxonomy = json.load(open(TAX))
    labels = load_labels()
    by_author = author_profiles(records, labels)

    sub_names = {s: n for top in taxonomy.values() for s, n in top["subs"].items()}
    top_of = {s: t for t, v in taxonomy.items() for s in v["subs"]}

    out, stats = [], collections.Counter()
    for idx, rec in enumerate(records):
        if idx in labels:
            sub, tags = labels[idx]
            confidence = "labeled"
        else:
            guess = infer_from_author(rec, by_author)
            if guess:
                sub, tags, confidence = guess, ["no-text", "inferred-from-author"], "inferred"
            else:
                sub = fallback_bucket(rec)
                tags = {"U1": ["x-article", "body-not-exported"],
                        "U2": ["media-only", "needs-vision"],
                        "U3": ["no-content"]}[sub]
                confidence = "unsorted"
        stats[confidence] += 1
        out.append({**rec,
                    "top": top_of[sub], "top_name": taxonomy[top_of[sub]]["name"],
                    "sub": sub, "sub_name": sub_names[sub],
                    "tags": tags, "confidence": confidence})

    json.dump(out, open(OUT, "w"))

    print(f"classified {len(out)} bookmarks: " +
          ", ".join(f"{n} {k}" for k, n in stats.most_common()))
    print()
    tops = collections.Counter(r["top"] for r in out)
    for code, n in tops.most_common():
        print(f"{taxonomy[code]['name']:<26} {n:>5}  {n/len(out)*100:4.1f}%")
        subs = collections.Counter(r["sub"] for r in out if r["top"] == code)
        for s, sn in subs.most_common():
            print(f"    {sub_names[s]:<40} {sn:>4}")


if __name__ == "__main__":
    build()
