"""Print a batch of records for labeling, or ingest labels back."""
import json, sys

REC = "/home/user/blank-app/data/records.json"
records = json.load(open(REC))
labelable = [(i, r) for i, r in enumerate(records) if len(r["text"]) >= 25]

if sys.argv[1] == "show":
    start, n = int(sys.argv[2]), int(sys.argv[3])
    for i, r in labelable[start:start + n]:
        t = r["text"][:230].replace("\t", " ")
        print(f"{i}|{t}")
elif sys.argv[1] == "count":
    print(len(labelable), "labelable;", "indices", labelable[0][0], "..", labelable[-1][0])
