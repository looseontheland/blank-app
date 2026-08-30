"""Emit a flat CSV of the organized library for spreadsheets / Notion / Airtable."""
import csv, json

items = json.load(open("data/classified.json"))
cols = ["id", "url", "date", "bucket", "sub_bucket", "tags", "confidence",
        "likes", "bookmarks", "has_media", "is_article", "signal", "text"]
with open("data/bookmarks.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(cols)
    for i in items:
        w.writerow([i["id"], i["url"], i["date"], i["top_name"], i["sub_name"],
                    ";".join(i["tags"]), i["confidence"], i["likes"], i["bookmarks"],
                    bool(i["media"]), i["is_article"], i["signal"], i["text"]])
print(f"wrote data/bookmarks.csv ({len(items)} rows)")
