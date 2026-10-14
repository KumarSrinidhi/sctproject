import sys
raw = open("work/rows_raw.jsonl","rb").read()
print("has_backslash_u:", b"\\u" in raw)
print("non_ascii_bytes:", sum(1 for b in raw if b > 127))
log = open("work/extraction_log.jsonl","rb").read()
print("log has_backslash_u:", b"\\u" in log, "non_ascii:", sum(1 for b in log if b > 127))
print("CRLF in rows_raw:", b"\r\n" in raw, "CRLF in log:", b"\r\n" in log)
