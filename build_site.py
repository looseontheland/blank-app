"""Phase 4b: bake the classified library into one self-contained HTML page."""
import collections, json, re

ITEMS = "/home/user/blank-app/data/classified.json"
TAX = "/home/user/blank-app/data/taxonomy.json"
TEMPLATE = "/home/user/blank-app/site/template.html"
OUT = "/home/user/blank-app/site/index.html"

CONF = {"labeled": 0, "inferred": 1, "unsorted": 2}


def build():
    items = json.load(open(ITEMS))
    taxonomy = json.load(open(TAX))

    # rows are positional to keep the payload small: the page rebuilds the
    # objects on load, and the tweet URL is derived from the id.
    rows = [[i["id"], i["date"], i["sub"], i["likes"], i["bookmarks"],
             len(i["media"]), CONF[i["confidence"]], ",".join(i["tags"]), i["text_display"]]
            for i in items]
    rows.sort(key=lambda r: r[1], reverse=True)

    tops = {c: v["name"] for c, v in taxonomy.items()}
    subs = {s: [c, n] for c, v in taxonomy.items() for s, n in v["subs"].items()}
    counts = collections.Counter(i["sub"] for i in items)

    payload = {"tops": tops, "subs": subs, "counts": counts, "rows": rows}
    blob = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    blob = blob.replace("</", "<\\/")  # never close the host <script> early

    html = open(TEMPLATE).read().replace("/*%%DATA%%*/", blob)
    open(OUT, "w").write(html)
    print(f"wrote {OUT}  ({len(html)/1e6:.2f} MB, {len(rows)} bookmarks)")


if __name__ == "__main__":
    build()
