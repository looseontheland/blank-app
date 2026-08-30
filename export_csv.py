"""Emit flat CSVs of the organized library for spreadsheets / Notion / Airtable.

Two files: the whole library with a `signal` column to filter on, and the
signal cut on its own for when you just want the good stuff in a sheet.
"""
import csv, json

items = json.load(open("data/classified.json"))
cols = ["id", "url", "date", "bucket", "sub_bucket", "tags", "confidence",
        "likes", "bookmarks", "has_media", "is_article", "signal", "text"]


def row(i):
    return [i["id"], i["url"], i["date"], i["top_name"], i["sub_name"],
            ";".join(i["tags"]), i["confidence"], i["likes"], i["bookmarks"],
            bool(i["media"]), i["is_article"], i["signal"], i["text"]]


def write(path, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(row(i) for i in rows)
    print(f"wrote {path} ({len(rows)} rows)")


write("data/bookmarks.csv", items)
write("data/bookmarks-signal.csv", [i for i in items if i["signal"]])
