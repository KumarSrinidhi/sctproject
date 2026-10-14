import json, sys
sys.stdout.reconfigure(encoding="utf-8")
log = [json.loads(l) for l in open("work/extraction_log.jsonl", encoding="utf-8")]
print("entries:", len(log))
print("last entry keys:", list(log[-1].keys()))
print("last entry:", json.dumps(log[-1], ensure_ascii=False)[:600])
tf = json.load(open("work/audit_phase2_inputs.json", encoding="utf-8"))["title_fixes"]
n = 0
for e in log:
    if e.get("doi") in tf:
        match = "CURRENT(wrong)" if e.get("paper_title") == tf[e["doi"]]["current"] else ("CORRECTED" if e.get("paper_title")==tf[e["doi"]]["corrected"] else "OTHER")
        n += 1
        print(f"log {e.get('candidate_id')} {e.get('doi')}: {match}")
print("log entries for fix DOIs:", n)
# check rej format
for e in log:
    r = e.get("rows_rejected_at_append")
    if r:
        print("rej sample:", e["candidate_id"], r)
        break
