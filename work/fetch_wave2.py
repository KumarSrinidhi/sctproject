import json, os, sys, re, time, urllib.request, urllib.parse, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fulltext')
os.makedirs(OUT_DIR, exist_ok=True)

TARGETS = [
    '10.3390/polym17111429', '10.3390/ma18214860', '10.3390/polym15061552',
    '10.3390/nano12030446', '10.3390/ma14185251', '10.3390/polym11081335',
    '10.3390/polym13020286', '10.1039/c9ra00282k', '10.3390/polym14142950',
    '10.3390/ma10121442', '10.3390/polym11101548', '10.3390/nano9101396',
    '10.3390/nano8120997', '10.3390/polym10030277', '10.3390/nano11081898',
    '10.1039/c8ra10645b', '10.1039/c8ra10211b', '10.3390/mi16101126',
    '10.3390/polym17111507', '10.3390/ma18215011', '10.3390/polym13132161',
    '10.3390/polym11010138', '10.3390/molecules28093797', '10.3390/polym18050648',
    '10.1007/s40820-023-01163-w', '10.3390/nano15120936', '10.3390/polym14061252',
    '10.3390/polym16081169', '10.3390/polym15051214', '10.3390/ijms24098221',
    '10.3390/polym13030456', '10.1039/c8ra03875a', '10.3390/polym12091913',
]

HDR = {'User-Agent': 'Mozilla/5.0 (research tool; mailto:research@example.org)'}


def fname(doi):
    return doi.replace('/', '_').replace('.', '_') if False else doi.replace('/', '_')


def fetch_url(url, timeout=60):
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def strip_xml(xml_text):
    # EPMC fullTextXML: keep table markers
    body = re.sub(r'<xref[^>]*>.*?</xref>', '', xml_text, flags=re.S)
    body = re.sub(r'</(p|title|td|tr|sec|abstract|table)>', '\n', body)
    body = re.sub(r'<td[^>]*>', ' | ', body)
    body = re.sub(r'<tr[^>]*>', '\n[ROW] ', body)
    body = re.sub(r'<table-wrap[^>]*>', '\n[TABLE]', body)
    body = re.sub(r'</table-wrap>', '[/TABLE]\n', body)
    body = re.sub(r'<fig[^>]*>', '\n[FIG] ', body)
    body = re.sub(r'<[^>]+>', ' ', body)
    body = re.sub(r'[ \t]+', ' ', body)
    body = re.sub(r'\n{3,}', '\n\n', body)
    return body


def epmc_fulltext(doi):
    # resolve PMCIDs via search
    q = 'DOI:"%s"' % doi
    url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
        {'query': q, 'format': 'json', 'pageSize': 5, 'resultType': 'core'})
    try:
        d = json.loads(fetch_url(url, timeout=45))
    except Exception as e:
        return None, f'search error {e}'
    for r in d.get('resultList', {}).get('result', []):
        pmcid = r.get('pmcid')
        if pmcid and (r.get('doi') or '').lower() == doi.lower():
            try:
                xml = fetch_url(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML', timeout=60)
                return strip_xml(xml.decode('utf-8', 'replace')), f'EPMC {pmcid}'
            except Exception as e:
                return None, f'xml error {e}'
    return None, 'no pmcid'


results = []
for doi in TARGETS:
    outp = os.path.join(OUT_DIR, fname(doi) + '.txt')
    if os.path.exists(outp) and os.path.getsize(outp) > 5000:
        print('skip (have)', doi)
        results.append((doi, 'have', ''))
        continue
    txt, how = epmc_fulltext(doi)
    if txt and len(txt) > 5000:
        with open(outp, 'w', encoding='utf-8') as f:
            f.write(f'SOURCE doi={doi} FETCH={how}\n' + txt)
        print('OK', doi, how, len(txt))
        results.append((doi, 'ok', how))
    else:
        print('FAIL', doi, how)
        results.append((doi, 'fail', how))
    time.sleep(0.3)

json.dump([dict(zip(('doi', 'status', 'how'), r)) for r in results],
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wave2_fetch.json'), 'w', encoding='utf-8'),
          indent=1)
ok = sum(1 for r in results if r[1] == 'ok')
print(f'done: {ok}/{len(TARGETS)} fetched')
