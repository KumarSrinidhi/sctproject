import json, sys
sys.stdout.reconfigure(encoding="utf-8")
rows = [json.loads(l) for l in open("work/rows_raw.jsonl", encoding="utf-8")]
for rid in ["bf4f3fd7-182","bf4f3fd7-183","caf49a8d-130","0e680d76-094","a9d63e6e-010"]:
    r = next(x for x in rows if x["row_id"]==rid)
    print(rid, json.dumps(r, ensure_ascii=False, indent=1))
    print()
# a8b6fee9 rows
print("a8b6fee9 rows:", [r["row_id"] for r in rows if r["row_id"].startswith("a8b6fee9")])
# per-DOI counts of any paper fully dropped
import collections
c = collections.Counter(r["doi"] for r in rows)
print("doi count for mi16101126:", c["10.3390/mi16101126"])
# Medium rows
print("Medium rows:", [(r["row_id"], r["doi"]) for r in rows if r["confidence"]=="Medium"])
# filler_loading_original_unit vocab
units = collections.Counter(r["filler_loading_original_unit"] for r in rows)
print("orig units:", units)
