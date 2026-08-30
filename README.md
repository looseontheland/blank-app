# 🔖 Bookmark Library

An organized, searchable archive of 3,443 X (Twitter) bookmarks spanning
2020–2026, sorted into 7 top-level buckets and 51 sub-buckets.

![buckets](https://img.shields.io/badge/bookmarks-3%2C443-blue) ![signal](https://img.shields.io/badge/signal-2%2C202-green)

## The buckets

| Bucket | All | Signal | What's in it |
|---|---|---|---|
| Health & Body | 886 | 873 | Gut/parasites/detox, supplements, hormones & peptides, hair & skin, bloodwork, nutrition, sleep, training |
| Business & Money | 727 | 542 | Cold email & lead gen, grayhat plays, case studies, SaaS, investing, tax & legal, offers & sales |
| AI & Tech | 591 | 401 | Agents & automation, AI creative, prompts, coding, industry news |
| Mind & Self | 416 | 113 | Mindset, psychology & inner work, dating, social skills, learning systems |
| Culture & Misc | 335 | 72 | Travel & geoarbitrage, memes, history, politics, gear |
| Marketing & Content | 254 | 201 | Content & video, paid ads, social growth, copywriting, funnels, SEO |
| Unsorted | 234 | 0 | Posts with no readable text (see caveats) |
| **Total** | **3,443** | **2,202** | |

## Signal vs. Everything

Both the site and the app open on **Signal** — 2,202 bookmarks that carry
something reusable — with **Everything** one click away.

Health & Body keeps everything readable; that shelf was already dense. The other
2,323 posts were read one at a time and kept only for a concrete procedure, a
named tool and how it fits, a copyable prompt or template, a teardown of why
something works, a case study with numbers *and* method, non-obvious domain
knowledge, or a real curated list. Cut: personal updates and flexes, motivation
with no method, promos and withheld-how teasers, context-free replies, memes,
and opinions with nothing behind them. Anything with no readable body is out of
Signal by definition.

The judgements live in `signal/cut*.txt` (record indices that did not make it);
`signal/README.md` has the full rubric. `build_classified.py` turns them into the
`signal` boolean carried by every record, the CSV, the app and the site.

## Run it

```
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Search full text, filter by bucket / sub-bucket / tag / year / media, sort by
date or engagement, and click through to the original post.

## Rebuilding from a fresh export

```
python build_records.py      # raw xarchive export -> data/records.json
python build_classified.py   # + labels/*.tsv + signal/cut*.txt -> data/classified.json
python export_csv.py         #  -> data/bookmarks.csv + data/bookmarks-signal.csv
python build_folders.py      #  -> export/Bookmark Library/ (a folder tree)
```

`build_folders.py` writes the library as folders to drop on a desktop: a folder
per shelf, a markdown file per sub-shelf, numbered biggest-first, with the
signal cut and the full library as parallel trees. It bundles the offline site
and the CSVs alongside them.

`labels/*.tsv` holds the classification itself, one line per bookmark:
`record_index <TAB> sub_bucket_code <TAB> comma,separated,tags`.
`data/taxonomy.json` defines the bucket codes and names.

## Caveats worth knowing

- **No author names.** Every `screen_name` in the export is `null` — only numeric
  user ids survived. Authors can be clustered, not named.
- **147 X Articles** are long-form posts where the export saved only the link;
  their bodies sit behind X's auth wall and could not be read.
- **80 media-only posts** carry their content in an image or video. The planned
  vision pass could not run: this machine's network policy blocks `pbs.twimg.com`.
- **73 items were filed by inference** — no usable text, so they inherit the
  bucket the rest of that author's bookmarks fall into. The app badges these as
  `inferred`; treat them as a guess.

Everything else (3,136 bookmarks) was filed by reading the post itself.

## The site

`site/index.html` is a single self-contained page — the whole library, searchable,
with no server and no build step at view time.

```
python build_site.py    # site/template.html + data/classified.json -> site/index.html
```

Open it directly, or serve the folder. Search full text, click a shelf to expand
its sub-shelves, click any tag or year to narrow, sort by date or engagement.
The View switch at the top of the rail flips between Signal and Everything —
the shelf counts, the tag cloud and the year chart all recount to match.
