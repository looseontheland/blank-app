"""Browser for an organized X (Twitter) bookmark archive."""
import collections
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st

DATA = Path(__file__).parent / "data"
PAGE_SIZE = 25

st.set_page_config(page_title="Bookmark Library", page_icon="🔖", layout="wide")


@st.cache_data
def load():
    items = json.load(open(DATA / "classified.json"))
    taxonomy = json.load(open(DATA / "taxonomy.json"))
    return items, taxonomy


items, taxonomy = load()

# ---------------------------------------------------------------- sidebar

st.sidebar.title("🔖 Bookmarks")
st.sidebar.caption(f"{len(items):,} saved posts, 2020–2026")

query = st.sidebar.text_input("Search", placeholder="taurine, cold email, seedance…")

top_names = {code: v["name"] for code, v in taxonomy.items()}
top_counts = collections.Counter(i["top"] for i in items)
top_choice = st.sidebar.multiselect(
    "Bucket",
    options=[c for c, _ in top_counts.most_common()],
    format_func=lambda c: f"{top_names[c]} ({top_counts[c]})",
)

# sub-buckets are offered only for the buckets actually in play
sub_pool = [i for i in items if not top_choice or i["top"] in top_choice]
sub_counts = collections.Counter(i["sub"] for i in sub_pool)
sub_names = {s: n for t in taxonomy.values() for s, n in t["subs"].items()}
sub_choice = st.sidebar.multiselect(
    "Sub-bucket",
    options=[s for s, _ in sub_counts.most_common()],
    format_func=lambda s: f"{sub_names[s]} ({sub_counts[s]})",
)

tag_counts = collections.Counter(t for i in sub_pool for t in i["tags"])
tag_choice = st.sidebar.multiselect(
    "Tags",
    options=[t for t, _ in tag_counts.most_common(400)],
    format_func=lambda t: f"{t} ({tag_counts[t]})",
)

years = sorted({i["date"][:4] for i in items})
year_choice = st.sidebar.multiselect("Year", options=years[::-1])

with st.sidebar.expander("More filters"):
    media_only = st.checkbox("Has image or video")
    thread_only = st.checkbox("Long posts only (1000+ chars)")
    hide_unsorted = st.checkbox("Hide unsorted", value=False)
    show_inferred = st.checkbox("Show confidence badges", value=True)

sort_by = st.sidebar.selectbox(
    "Sort", ["Newest first", "Oldest first", "Most liked", "Most bookmarked"]
)

# ---------------------------------------------------------------- filtering


def matches(item):
    if top_choice and item["top"] not in top_choice:
        return False
    if sub_choice and item["sub"] not in sub_choice:
        return False
    if tag_choice and not set(tag_choice) & set(item["tags"]):
        return False
    if year_choice and item["date"][:4] not in year_choice:
        return False
    if media_only and not item["media"]:
        return False
    if thread_only and len(item["text"]) < 1000:
        return False
    if hide_unsorted and item["top"] == "U":
        return False
    if query:
        haystack = (item["text"] + " " + " ".join(item["tags"]) + " "
                    + item["sub_name"]).lower()
        if not all(term in haystack for term in query.lower().split()):
            return False
    return True


results = [i for i in items if matches(i)]

sort_key = {
    "Newest first": lambda i: i["date"],
    "Oldest first": lambda i: i["date"],
    "Most liked": lambda i: i["likes"],
    "Most bookmarked": lambda i: i["bookmarks"],
}[sort_by]
results.sort(key=sort_key, reverse=sort_by != "Oldest first")

# ---------------------------------------------------------------- main

tab_browse, tab_map, tab_about = st.tabs(["Browse", "The map", "About this archive"])

with tab_browse:
    st.markdown(f"### {len(results):,} bookmarks")
    if not results:
        st.info("Nothing matches those filters. Try clearing one.")
    else:
        pages = (len(results) - 1) // PAGE_SIZE + 1
        page = 1
        if pages > 1:
            page = st.number_input(
                f"Page (1–{pages})", 1, pages, 1, label_visibility="collapsed"
            )
        for item in results[(page - 1) * PAGE_SIZE: page * PAGE_SIZE]:
            badge = ""
            if show_inferred and item["confidence"] != "labeled":
                badge = f" · :orange[{item['confidence']}]"
            st.markdown(
                f"**{item['sub_name']}**  ·  {item['date']}  ·  "
                f"♥ {item['likes']:,}  ·  🔖 {item['bookmarks']:,}{badge}"
            )
            body = item["text"] or "_(no text — image, video, or X Article)_"
            if len(body) > 900:
                st.write(body[:900] + "…")
                with st.expander("Read the rest"):
                    st.write(body)
            else:
                st.write(body)
            chips = " ".join(f"`{t}`" for t in item["tags"])
            st.markdown(f"{chips} &nbsp; [open on X →]({item['url']})")
            st.divider()

with tab_map:
    st.markdown("### What's in the library")
    counts = collections.Counter(i["top"] for i in items)
    cols = st.columns(4)
    for col, (code, n) in zip(cols * 2, counts.most_common(4)):
        col.metric(top_names[code], f"{n:,}",
                   f"{n / len(items) * 100:.0f}% of library", delta_color="off")

    frame = pd.DataFrame(
        [{"Bucket": top_names[i["top"]], "Sub-bucket": i["sub_name"]} for i in items]
    )
    summary = (frame.groupby(["Bucket", "Sub-bucket"]).size()
               .reset_index(name="Bookmarks")
               .sort_values(["Bucket", "Bookmarks"], ascending=[True, False]))
    st.dataframe(summary, use_container_width=True, hide_index=True)

    st.markdown("### Saved per year")
    per_year = pd.Series(collections.Counter(i["date"][:4] for i in items)).sort_index()
    st.bar_chart(per_year)

    st.markdown("### Most used tags")
    tags = collections.Counter(t for i in items for t in i["tags"]).most_common(40)
    st.dataframe(pd.DataFrame(tags, columns=["Tag", "Bookmarks"]),
                 use_container_width=True, hide_index=True)

with tab_about:
    counts = collections.Counter(i["confidence"] for i in items)
    st.markdown(f"""
### Where this came from

An `xarchive` export of **{len(items):,} X bookmarks** (2020-09-29 → 2026-08-30),
sorted into {len(taxonomy)} top-level buckets and
{sum(len(v['subs']) for v in taxonomy.values())} sub-buckets.

### How confident each label is

- **{counts['labeled']:,} labeled** — the post's own text was read and filed.
- **{counts['inferred']:,} inferred** — the post has no usable text, so it was
  filed by looking at where the rest of that author's bookmarks landed. Treat
  these as a guess.
- **{counts['unsorted']:,} unsorted** — no text to go on and no confident guess.

### Two things the export could not give us

1. **No author names.** Every `screen_name` in the export is `null`; only numeric
   user ids survived. Authors can be clustered but not named.
2. **No X Article bodies.** {sum(1 for i in items if i['is_article'])} bookmarks
   are long-form X Articles where the export captured only the link. Their text
   lives behind X's auth wall.

Image and video posts could not be read either — this machine's network policy
blocks `pbs.twimg.com`, so the planned vision pass never ran.
""")
