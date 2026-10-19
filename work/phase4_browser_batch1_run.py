import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from phase4_browser_save import save
recs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phase4_browser_batch1.json'), encoding='utf-8'))
for r in recs:
    save(r['doi'], r['text'])
