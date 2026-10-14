import json, os, re, time, csv, urllib.request, urllib.parse

UA_XML = 'research-agent/1.0 (mailto:research@example.org)'
UA_BROWSER = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
os.makedirs(FT, exist_ok=True)

CAPTCHA = ('radware', 'captcha', 'enable javascript', 'access denied',
           'request unsuccessful', 'incapsula', 'cf-browser-verification')


def get(url, ua=UA_XML, timeout=60, tries=2):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.headers.get('Content-Type', '')
        except Exception as e:
            last = e
            time.sleep(2 + 2 * i)
    raise last


def xml_to_text(xml_bytes):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml_bytes, 'lxml-xml')
    out = []
    t = soup.find('article-title')
    if t:
        out.append('TITLE: ' + t.get_text(' ', strip=True))
    ab = soup.find('abstract')
    if ab:
        out.append('\nABSTRACT:\n' + ab.get_text(' ', strip=True))
    body = soup.find('body')
    if body:
        for sec in body.find_all('sec'):
            title = sec.find('title', recursive=False)
            if title:
                out.append('\n## ' + title.get_text(' ', strip=True))
            for child in sec.children:
                name = getattr(child, 'name', None)
                if name == 'p':
                    out.append(child.get_text(' ', strip=True))
                elif name in ('table-wrap', 'fig'):
                    out.append(render_block(child, name))
    for tw in soup.find_all('table-wrap'):
        if body and tw in body:
            continue
        out.append(render_block(tw, 'table-wrap'))
    return '\n'.join(out)


def render_block(el, name):
    lines = []
    if name == 'table-wrap':
        lab = el.find('label'); cap = el.find('caption')
        hdr = (lab.get_text(' ', strip=True) if lab else 'Table')
        if cap:
            hdr += ': ' + cap.get_text(' ', strip=True)
        lines.append('\n[TABLE] ' + hdr)
        tbl = el.find('table')
        if tbl:
            for tr in tbl.find_all('tr'):
                cells = [c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])]
                lines.append(' | '.join(cells))
        fn = el.find('table-wrap-foot')
        if fn:
            lines.append('[FOOT] ' + fn.get_text(' ', strip=True))
        lines.append('[/TABLE]')
    elif name == 'fig':
        lab = el.find('label'); cap = el.find('caption')
        lines.append('\n[FIG] ' + (lab.get_text(' ', strip=True) if lab else '') + ': ' +
                     (cap.get_text(' ', strip=True) if cap else ''))
    return '\n'.join(lines)


def pdf_to_text(path):
    import fitz
    doc = fitz.open(path)
    out = []
    for i, page in enumerate(doc):
        out.append(f'\n===== PAGE {i+1} =====')
        try:
            tabs = page.find_tables()
            for t in tabs.tables:
                data = t.extract()
                if data and len(data) > 1:
                    out.append(f'[TABLE p{i+1}]')
                    for row in data:
                        out.append(' | '.join('' if c is None else str(c).replace('\n', ' ') for c in row))
                    out.append('[/TABLE]')
            out.append(page.get_text('text'))
        except Exception:
            out.append(page.get_text('text'))
    doc.close()
    return '\n'.join(out)


def slug(doi):
    return re.sub(r'[^A-Za-z0-9._-]', '_', doi)[:90]


def looks_blocked(text):
    low = text[:4000].lower()
    return any(c in low for c in CAPTCHA)


# ---------- build DOI work list ----------
rows = [json.loads(l) for l in open(os.path.join(BASE, 'rows_raw.jsonl'), encoding='utf-8')]
have = {r['doi'].lower() for r in rows}

targets = {}   # doi -> meta

with open(os.path.join(BASE, '..', 'unusable_sources.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        if r['action'].startswith('unusable'):
            targets[r['doi'].lower()] = {'reason': 'unusable_sources', 'meta': {}}

cands = json.load(open(os.path.join(BASE, 'candidates.json'), encoding='utf-8'))
for c in cands:
    d = (c.get('doi') or '').lower()
    if not d or d in have:
        continue
    if d in targets:
        targets[d]['meta'] = c
        continue
    if c.get('is_oa') or c.get('oa_status') in ('gold', 'bronze', 'green', 'hybrid') or c.get('pmcid'):
        targets[d] = {'reason': 'oa_candidate', 'meta': c}
    else:
        targets[d] = {'reason': 'candidate_epmc_probe', 'meta': c}

print('target DOIs:', len(targets))
order = ([d for d, v in targets.items() if v['reason'] == 'unusable_sources'] +
         [d for d, v in targets.items() if v['reason'] == 'oa_candidate'] +
         [d for d, v in targets.items() if v['reason'] == 'candidate_epmc_probe'])

log_path = os.path.join(BASE, 'phase3_fetch_log.json')
log = []
if os.path.exists(log_path):
    log = json.load(open(log_path, encoding='utf-8'))
done = {e['doi'] for e in log if e.get('outcome')}

for n, doi in enumerate(order, 1):
    if n % 10 == 0:
        json.dump(log, open(log_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if doi in done:
        continue
    meta = targets[doi]['meta']
    path = os.path.join(FT, slug(doi) + '.txt')
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        txt = open(path, encoding='utf-8', errors='replace').read()
        if not looks_blocked(txt):
            log.append(dict(doi=doi, route='local', outcome='already_exists', chars=len(txt),
                            reason=targets[doi]['reason']))
            continue
    entry = dict(doi=doi, reason=targets[doi]['reason'], route='', outcome='', chars=0, note='')

    # ---- Route 1: Europe PMC by DOI ----
    try:
        u = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=' +
             urllib.parse.quote('DOI:"%s"' % doi) + '&format=json&resultType=core')
        raw, _ = get(u)
        res = json.loads(raw).get('resultList', {}).get('result', [])
        pmcid = None
        for r0 in res:
            if (r0.get('doi') or '').lower() == doi or not res:
                pmcid = r0.get('pmcid')
                meta.setdefault('title', r0.get('title'))
                meta.setdefault('year', r0.get('pubYear'))
                meta.setdefault('journal', r0.get('journalTitle'))
                break
        if res and not pmcid:
            pmcid = res[0].get('pmcid')
        if pmcid:
            entry['route'] = 'epmc_xml:' + pmcid
            raw2, _ = get('https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextXML' % pmcid)
            txt = xml_to_text(raw2)
            if len(txt) > 3000 and not looks_blocked(txt):
                header = ('SOURCE doi=%s FETCH=EPMC %s\nTITLE: %s\nYEAR: %s\nJOURNAL: %s\n\n'
                          % (doi, pmcid, meta.get('title', ''), meta.get('year', ''),
                             meta.get('journal', '')))
                open(path, 'w', encoding='utf-8').write(header + txt)
                entry.update(outcome='saved', chars=len(txt))
                log.append(entry)
                print('[%d/%d] SAVED %s %d chars' % (n, len(order), doi, len(txt)))
                continue
            entry['note'] = 'epmc xml too short/blocked (%d)' % len(txt)
        else:
            entry['note'] = 'not in EPMC'
    except Exception as e:
        entry['note'] = 'epmc fail: %s' % str(e)[:80]

    # ---- Route 2: Unpaywall OA locations ----
    links0 = []
    try:
        raw, _ = get('https://api.unpaywall.org/v2/%s?email=research@example.org' % doi,
                     timeout=30, tries=1)
        up = json.loads(raw)
        for loc in (up.get('oa_locations') or []):
            for k in ('url_for_pdf', 'url'):
                if loc.get(k):
                    links0.append(loc[k])
    except Exception as e:
        entry['note'] = (entry['note'] + ' | ').strip(' |') + 'unpaywall fail: %s' % str(e)[:60]

    # ---- Route 3: known OA links (candidates) ----
    for k in ('oa_url', 'oa_pdf_url'):
        if meta.get(k):
            links0.append(meta[k])
    for l in (meta.get('fulltext_links') or []):
        links0.append(l)
    links, seen = [], set()
    for u in links0:
        if u and u not in seen:
            seen.add(u); links.append(u)
    saved = False
    BLOCKED_HOSTS = ('wiley.com', 'sciencedirect.com', 'elsevier.com', 'springer.com',
                     'tandfonline.com', 'iopscience.iop.org', 'acs.org', 'pubs.rsc.org',
                     'aip.org', 'ieee.org', 'degruyter.com', 'cambridge.org', 'nature.com',
                     'science.org', 'rsc.org', 'scielo', 'hindawi.com')
    for u in links[:3]:
        host = u.split('/')[2]
        if any(b in host for b in BLOCKED_HOSTS):
            entry['note'] = (entry['note'] + ' | ').strip(' |') + 'skip blocked host %s' % host
            continue
        try:
            raw, ct = get(u, ua=UA_BROWSER, timeout=35, tries=1)
            body = None
            if 'pdf' in (ct or '') or u.lower().endswith('.pdf'):
                tmp = os.path.join(FT, slug(doi) + '.tmp.pdf')
                open(tmp, 'wb').write(raw)
                body = pdf_to_text(tmp)
                try:
                    os.remove(tmp)
                except Exception:
                    pass
            else:
                from bs4 import BeautifulSoup
                html_txt = raw.decode('utf-8', 'replace')
                if looks_blocked(html_txt[:6000]):
                    entry['note'] = 'blocked: %s' % u.split('/')[2]
                    continue
                soup = BeautifulSoup(raw, 'lxml')
                for bad in soup(['script', 'style', 'nav', 'header', 'footer']):
                    bad.decompose()
                lines = []
                for el in soup.find_all(['h1', 'h2', 'h3', 'p', 'table', 'figcaption']):
                    if el.name == 'table':
                        lines.append('[TABLE]')
                        for tr in el.find_all('tr'):
                            cells = [c2.get_text(' ', strip=True) for c2 in tr.find_all(['td', 'th'])]
                            lines.append(' | '.join(cells))
                        lines.append('[/TABLE]')
                    elif el.name == 'figcaption':
                        lines.append('[FIG] ' + el.get_text(' ', strip=True))
                    else:
                        lines.append(el.get_text(' ', strip=True))
                body = '\n'.join(lines)
            if body and len(body) > 3000:
                header = ('SOURCE doi=%s FETCH=%s\nTITLE: %s\nYEAR: %s\nJOURNAL: %s\n\n'
                          % (doi, u.split('/')[2], meta.get('title', ''), meta.get('year', ''),
                             meta.get('journal', '')))
                open(path, 'w', encoding='utf-8').write(header + body)
                entry.update(route='direct:' + u.split('/')[2], outcome='saved', chars=len(body))
                log.append(entry)
                print('[%d/%d] SAVED %s %d chars (%s)' % (n, len(order), doi, len(body), u.split('/')[2]))
                saved = True
                break
        except Exception as e:
            entry['note'] = (entry['note'] + ' | ').strip(' |') + 'link fail %s: %s' % (
                u.split('/')[2], str(e)[:60])
    if saved:
        continue

    entry.setdefault('route', entry['route'] or 'none')
    entry['outcome'] = 'blocked' if entry['note'] else 'no_fulltext'
    log.append(entry)
    if n % 10 == 0:
        json.dump(log, open(log_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    if n % 25 == 0:
        print('... %d/%d processed' % (n, len(order)))
    time.sleep(0.15)

json.dump(log, open(log_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
saved_n = sum(1 for e in log if e.get('outcome') == 'saved')
print('DONE. saved=%d, log entries=%d' % (saved_n, len(log)))
