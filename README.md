# 🔖 Bookmark Library

An organized, searchable archive of 3,443 X (Twitter) bookmarks spanning
2020–2026, sorted into 7 top-level buckets and 51 sub-buckets.

![buckets](https://img.shields.io/badge/bookmarks-3%2C443-blue)

## The buckets

| Bucket | Share | What's in it |
|---|---|---|
| Health & Body | 26% | Gut/parasites/detox, supplements, hormones & peptides, hair & skin, bloodwork, nutrition, sleep, training |
| Business & Money | 21% | Cold email & lead gen, grayhat plays, case studies, SaaS, investing, tax & legal, offers & sales |
| AI & Tech | 17% | Agents & automation, AI creative, prompts, coding, industry news |
| Mind & Self | 12% | Mindset, psychology & inner work, dating, social skills, learning systems |
| Culture & Misc | 10% | Travel & geoarbitrage, memes, history, politics, gear |
| Marketing & Content | 7% | Content & video, paid ads, social growth, copywriting, funnels, SEO |
| Unsorted | 7% | Posts with no readable text (see caveats) |

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
python build_classified.py   # + labels/*.tsv       -> data/classified.json
python export_csv.py         #                      -> data/bookmarks.csv
```

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
