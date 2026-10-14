import sys, re
sys.stdout.reconfigure(encoding="utf-8")
qc = open("quality_control_report.md", encoding="utf-8").read()
for line in qc.splitlines():
    if re.match(r"\| (Total rows|Unique papers|Year range|k_composite range|Median k|High|Medium|Text|Table|Epoxy-based|Silicone|Polyimide) \|", line):
        print(line)
print("---- section 8 head ----")
i = qc.index("## 8.")
print(qc[i:i+1400])
