import json, sys
sys.stdout.reconfigure(encoding="utf-8")
p1 = json.load(open("work/audit_phase1_rows.json", encoding="utf-8"))
for rid in ["fa7ce3db-036","3bde4e56-147","544349ee-180","f02bb9ff-095","4a11b03c-151","4a11b03c-152","4a11b03c-153","031e3932-188"]:
    for r in p1["rows"]:
        if r["row_id"] == rid:
            print(rid, "|", r["verification_status"])
            for f in r.get("findings", []):
                print("   -", f)
            print()
