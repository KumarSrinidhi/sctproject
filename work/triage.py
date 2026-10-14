import json, time, urllib.request, urllib.parse, os

UA = 'research-agent/1.0 (mailto:research@example.org)'
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'candidates.json')
cands = json.load(open(path, encoding='utf-8'))

def fetch(url, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tries - 1:
                return None
            time.sleep(2 * (i + 1))

doi_count = 0
for c in cands:
    doi = c.get('doi')
    if not doi:
        continue
    doi_count += 1
    txt = fetch('https://api.unpaywall.org/v2/' + urllib.parse.quote(doi) + '?email=research@example.org')
    if txt:
        try:
            d = json.loads(txt)
        except Exception:
            d = {}
        c['is_oa'] = d.get('is_oa')
        c['oa_status'] = d.get('oa_status')
        b = d.get('best_oa_location') or {}
        c['oa_url'] = b.get('url')
        c['oa_pdf_url'] = b.get('url_for_pdf')
        c['oa_host'] = b.get('host_type')
        c['oa_version'] = b.get('version')
        c['oa_license'] = b.get('license')
        if not c.get('fulltext_links'):
            c['fulltext_links'] = []
        if b.get('url') and b['url'] not in c['fulltext_links']:
            c['fulltext_links'].append(b['url'])
        if b.get('url_for_pdf') and b['url_for_pdf'] not in c['fulltext_links']:
            c['fulltext_links'].append(b['url_for_pdf'])
    else:
        c['is_oa'] = None
    time.sleep(0.25)

# keep earlier fields too
n_oa = sum(1 for c in cands if c.get('is_oa'))
print('DOIs checked:', doi_count, '| OA:', n_oa)
json.dump(cands, open(path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

# summarize access routes
import collections
hosts = collections.Counter()
for c in cands:
    if c.get('is_oa'):
        u = c.get('oa_url') or ''
        m = None
        for dom in ['mdpi.com', 'ncbi.nlm.nih.gov', 'rsc.org', 'nature.com', 'frontiersin', 'wiley.com',
                    'sciencedirect.com', 'springer.com', 'acs.org', 'iopscience', 'aip.org',
                    'arxiv.org', 'chemrxiv.org', 'zenodo.org', 'figshare.com', 'researchgate.net',
                    'tandfonline.com', 'degruyter.com', 'hindawi.com', 'peerj.com', 'jstage']:
            if dom in u:
                m = dom; break
        hosts[m or ('other:' + u.split('/')[2] if '://' in u else '?')] += 1
print(hosts.most_common(30))
