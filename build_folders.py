"""Emit the library as a folder tree you can drop on a desktop.

Mirrors the site: a folder per shelf, a markdown file per sub-shelf, ordered
by size so the biggest shelves sort first. Two trees — the signal cut and the
whole library — plus a per-shelf CSV for anything you'd rather open in a sheet.
"""
import collections, csv, json, pathlib, re, shutil

DATA = pathlib.Path("data")
OUT = pathlib.Path("export/Bookmark Library")

TOP_ORDER = ["H", "B", "A", "S", "C", "M", "U"]
CSV_COLS = ["date", "bucket", "sub_bucket", "tags", "likes", "bookmarks", "url", "text"]


def safe(name):
    """Filename-safe on macOS, Windows and Linux alike."""
    name = re.sub(r'[<>:"/\\|?*]', "-", name)
    return re.sub(r"\s+", " ", name).strip().rstrip(".")


def hard_breaks(text):
    """Most of these posts are lists. Markdown eats single newlines, so end
    every line that has another line under it with an explicit break."""
    lines = text.split("\n")
    return "\n".join(
        ln + "  " if ln.strip() and i + 1 < len(lines) and lines[i + 1].strip() else ln
        for i, ln in enumerate(lines)
    )


def entry(rec):
    """One bookmark as a markdown block, keeping the post's own line breaks."""
    head = f"### {rec['date']}  ·  {rec['likes']:,} likes  ·  {rec['bookmarks']:,} saves"
    if rec["media"]:
        head += f"  ·  {len(rec['media'])} media"
    if rec["confidence"] != "labeled":
        head += f"  ·  _{rec['confidence']}_"
    body = hard_breaks(rec["text_display"].strip()) or \
        "_No text — the post is an image, a video, or an X Article._"
    tags = ", ".join(f"`{t}`" for t in rec["tags"])
    return f"{head}\n\n{body}\n\n{tags}\n\n[open on X →]({rec['url']})\n"


def write_tree(root, items, taxonomy, label):
    sub_names = {s: n for t in taxonomy.values() for s, n in t["subs"].items()}
    by_top = collections.defaultdict(list)
    for i in items:
        by_top[i["top"]].append(i)

    ranked = [t for t in TOP_ORDER if by_top[t]]
    ranked.sort(key=lambda t: -len(by_top[t]))

    lines = [f"# {label}", "", f"{len(items):,} bookmarks.", ""]
    for n, top in enumerate(ranked, 1):
        shelf = by_top[top]
        folder = root / f"{n} {safe(taxonomy[top]['name'])}"
        folder.mkdir(parents=True, exist_ok=True)
        lines.append(f"- **{taxonomy[top]['name']}** — {len(shelf):,}")

        by_sub = collections.defaultdict(list)
        for i in shelf:
            by_sub[i["sub"]].append(i)

        for sub, posts in sorted(by_sub.items(), key=lambda kv: -len(kv[1])):
            posts.sort(key=lambda i: i["date"], reverse=True)
            name = sub_names[sub]
            path = folder / f"{safe(name)}.md"
            path.write_text(
                f"# {name}\n\n"
                f"{len(posts):,} bookmarks · {taxonomy[top]['name']} · newest first\n\n"
                "---\n\n" + "\n---\n\n".join(entry(p) for p in posts) + "\n"
            )
            lines.append(f"  - {name} — {len(posts):,}")

        with open(folder / f"_{safe(taxonomy[top]['name'])}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(CSV_COLS)
            for i in sorted(shelf, key=lambda i: i["date"], reverse=True):
                w.writerow([i["date"], i["top_name"], i["sub_name"], ";".join(i["tags"]),
                            i["likes"], i["bookmarks"], i["url"], i["text"]])

    (root / "Contents.md").write_text("\n".join(lines) + "\n")
    return ranked


def build():
    items = json.load(open(DATA / "classified.json"))
    taxonomy = json.load(open(DATA / "taxonomy.json"))
    signal = [i for i in items if i["signal"]]

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    write_tree(OUT / "Signal", signal, taxonomy, "Signal")
    write_tree(OUT / "Everything", items, taxonomy, "Everything")

    for src, dst in [(DATA / "bookmarks.csv", "bookmarks.csv"),
                     (DATA / "bookmarks-signal.csv", "bookmarks-signal.csv"),
                     (pathlib.Path("site/index.html"), "Bookmark Library.html")]:
        if src.exists():
            shutil.copy(src, OUT / dst)

    (OUT / "README.md").write_text(f"""# Bookmark Library

{len(items):,} X bookmarks saved between September 2020 and August 2026, read
one at a time and filed into 7 shelves and 51 sub-shelves.

## What's here

- **`Bookmark Library.html`** — the whole thing as a searchable page. Double-click
  it; it works offline, no server, no internet. Start here.
- **`Signal/`** — the {len(signal):,} bookmarks that carry something reusable, one
  folder per shelf, one markdown file per sub-shelf, newest post first.
- **`Everything/`** — the same tree over all {len(items):,}.
- **`bookmarks.csv` / `bookmarks-signal.csv`** — flat exports for a spreadsheet.
- **`Contents.md`** inside each tree — the shelf list with counts.
- **`_<Shelf>.csv`** inside each shelf folder — just that shelf, for a sheet.

Folders are numbered by size, so `1` is the biggest shelf.

## Signal vs. Everything

Health & Body keeps everything readable — that shelf was already dense. The
other 2,323 posts were read one at a time and kept only for a concrete
procedure, a named tool and how it fits, a copyable prompt or template, a
teardown of why something works, a case study with numbers *and* method,
non-obvious domain knowledge, or a real curated list. Cut: personal updates and
flexes, motivation with no method, promos and withheld-how teasers, context-free
replies, memes, and opinions with nothing behind them. Anything with no readable
body is out of Signal by definition.

## Two limits from the export

X's export left every author's screen name `null`, so no post here is
attributed. It also saved only the link for long-form X Articles, and the text
inside images and videos could not be read — those posts sit under Unsorted in
the Everything tree and are absent from Signal.
""")

    files = sum(1 for _ in OUT.rglob("*") if _.is_file())
    size = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"wrote {OUT}  ({files} files, {size/1e6:.1f} MB)")


if __name__ == "__main__":
    build()
