"""Phase 1: normalize the raw xarchive export into flat records for classification."""
import json, re, sys, collections

SRC = "/root/.claude/uploads/53fe7b11-e2c5-5747-aaca-ae5c526167a0/05d1357f-xarchive_yzbrrr_20260830.json"
OUT = "/home/user/blank-app/data/records.json"

MONTHS = {m: i for i, m in enumerate(
    "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split(), 1)}


def iso_date(created):
    # "Tue Sep 29 01:26:10 +0000 2020" -> "2020-09-29"
    p = created.split()
    return f"{p[-1]}-{MONTHS[p[1]]:02d}-{int(p[2]):02d}"


def strip_tco(t):
    return re.sub(r"https://t\.co/\w+", "", t or "")


def build():
    raw = json.load(open(SRC))
    records = []
    for b in raw["bookmarks"]:
        if b.get("status") != "available":
            continue
        quoted = b.get("quoted_tweet") or {}
        own = " ".join(strip_tco(b.get("full_text")).split())
        qt = " ".join(strip_tco(quoted.get("full_text")).split())
        urls = [u.get("expanded_url") or "" for u in b["entities"].get("urls", [])]
        card = b.get("card") or {}
        card_text = " ".join(
            x for x in (card.get("title"), card.get("description")) if x)

        # the text a classifier actually gets to see
        text = own
        if qt:
            text += f"  [quoting: {qt}]"
        if card_text:
            text += f"  [link: {card_text}]"
        text = " ".join(text.split())

        article_urls = [u for u in urls if "/i/article/" in u]
        media = [m["url"] for m in b.get("media") or []]

        records.append({
            "id": b["tweet_id"],
            "url": f"https://x.com/i/status/{b['tweet_id']}",
            "date": iso_date(b["created_at"]),
            "text": text,
            "own_text": own,
            "quoted_text": qt,
            "author_id": (b.get("author") or {}).get("user_id"),
            "lang": b.get("lang"),
            "likes": b["metrics"]["likes"],
            "bookmarks": b["metrics"]["bookmarks"],
            "media": media,
            "media_types": [m["type"] for m in b.get("media") or []],
            "urls": [u for u in urls if u],
            "is_article": bool(article_urls),
            "conversation_id": b["conversation_id"],
        })

    records.sort(key=lambda r: r["date"])
    json.dump(records, open(OUT, "w"), indent=1)

    # routing summary: which items need which treatment
    thin = [r for r in records if len(r["text"]) < 25]
    print(f"records:            {len(records)}")
    print(f"  labelable by text: {len(records) - len(thin)}")
    print(f"  thin text total:   {len(thin)}")
    print(f"    x articles:      {sum(1 for r in thin if r['is_article'])}")
    print(f"    media-only:      {sum(1 for r in thin if not r['is_article'] and r['media'])}")
    print(f"    truly empty:     {sum(1 for r in thin if not r['is_article'] and not r['media'])}")
    print(f"  unique authors:    {len(set(r['author_id'] for r in records))}")
    print(f"  date range:        {records[0]['date']} .. {records[-1]['date']}")


if __name__ == "__main__":
    build()
