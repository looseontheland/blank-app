# The signal cut

The Signal view is a hand-judged subset of the library. Every one of the 2,323
non-health bookmarks was read and judged individually against the rubric below;
`cut000.txt` … `cut006.txt` list the record indices that did **not** make it
(whitespace-separated, one batch per file). `build_classified.py` turns those
into the `signal` boolean on every record.

## Rules

- **Health & Body keeps everything** that had a readable body. Per the owner:
  the health shelf is already dense — the noise problem lives elsewhere.
- **Anything with no readable body is out.** X-article stubs, media-only posts
  and the author-inferred items render as blank cards, so they carry nothing.
- **Everything else has to earn its place.**

## Rubric for the other five shelves

**Keep** when the post carries something reusable:

- a concrete procedure, protocol or step list
- a named tool or stack, with how it fits
- a copyable template, prompt or script
- a teardown that explains *why* a mechanism works
- a case study with both numbers **and** method
- non-obvious domain knowledge
- a real curated resource list (books, repos, people, niches)

**Cut** when it is:

- a personal update, milestone or flex
- generic motivation with no method
- a promo, teaser, or "here's how 👇" with the how withheld
- a context-free reply or quote-tweet reaction
- a meme or joke
- a vague opinion with no evidence behind it

## Result

| Shelf | In library | In signal |
|---|---|---|
| Health & Body | 886 | 873 |
| Business & Money | 727 | 542 |
| AI & Tech | 591 | 401 |
| Marketing & Content | 254 | 201 |
| Mind & Self | 416 | 113 |
| Culture & Misc | 335 | 72 |
| Unsorted | 234 | 0 |
| **Total** | **3,443** | **2,202** |

Mind & Self and Culture & Misc take the heaviest cuts — that is where the
motivational one-liners, the flexes and the memes live.
