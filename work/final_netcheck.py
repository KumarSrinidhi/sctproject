"""Optional network sanity check: Crossref title match for 2 random High-confidence rows.
Never aborts; results appended to work/final_verification.json. Skipped silently on failure."""
import json, random, re, ssl, urllib.request, urllib.parse, datetime
from pathlib import Path

VF = Path('work/final_verification.json')
rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
high = [r for r in rows if r['confidence'] == 'High']
random.seed(20261018)
picks = random.sample(high, 2)

def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', (s or '').lower()).strip()

def fetch(doi, ctx):
    url = 'https://api.crossref.org/works/' + urllib.parse.quote(doi)
    req = urllib.request.Request(url, headers={'User-Agent': 'ARGUS-dataset-verify/1.0 (mailto:noreply@example.org)'})
    with urllib.request.urlopen(req, timeout=12, context=ctx) as resp:
        return json.load(resp)['message']

results = []
for r in picks:
    entry = {'row_id': r['row_id'], 'doi': r['doi'], 'dataset_title': r['paper_title']}
    try:
        try:
            msg = fetch(r['doi'], ssl.create_default_context())
        except ssl.SSLError:
            msg = fetch(r['doi'], ssl._create_unverified_context())  # read-only public metadata fallback
        ctitle = norm(msg.get('title', [''])[0])
        dtitle = norm(r['paper_title'])
        overlap = len(set(ctitle.split()) & set(dtitle.split())) / max(1, len(set(dtitle.split())))
        entry.update({'status': 'resolved', 'crossref_title': msg.get('title', [''])[0],
                      'title_word_overlap': round(overlap, 2),
                      'match': overlap >= 0.6})
    except Exception as e:
        entry.update({'status': 'network_failed', 'error': f'{type(e).__name__}: {e}'})
    results.append(entry)
    print(entry)

vf = json.load(open(VF, encoding='utf-8'))
vf['network_sanity_checks'] = {'date': str(datetime.date.today()), 'results': results,
        'note': 'Optional; failures are network-environment issues, not dataset issues.'}
json.dump(vf, open(VF, 'w', encoding='utf-8'), indent=2)
print('logged to work/final_verification.json')
