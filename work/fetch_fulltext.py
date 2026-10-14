import json, os, re, time, urllib.request, urllib.parse, html as htmlmod

UA_XML = 'research-agent/1.0 (mailto:research@example.org)'
UA_BROWSER = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
os.makedirs(FT, exist_ok=True)
CAND = os.path.join(BASE, 'candidates.json')
cands = json.load(open(CAND, encoding='utf-8'))

def get(url, ua=UA_XML, timeout=90, tries=2):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': ua, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.headers.get('Content-Type', '')
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3)

def xml_to_text(xml_bytes):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(xml_bytes, 'lxml-xml')
    out = []
    # title
    t = soup.find('article-title')
    if t:
        out.append('TITLE: ' + t.get_text(' ', strip=True))
    # abstract
    ab = soup.find('abstract')
    if ab:
        out.append('\nABSTRACT:\n' + ab.get_text(' ', strip=True))
    # body sections with tables inline
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
    # floats outside body (some tables)
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
            tbl_spans = []
            for t in tabs.tables:
                data = t.extract()
                if data and len(data) > 1:
                    out.append(f'[TABLE p{i+1}]')
                    for row in data:
                        out.append(' | '.join('' if c is None else str(c).replace('\n', ' ') for c in row))
                    out.append('[/TABLE]')
                    tbl_spans.extend(t.bbox and [t.bbox] or [])
            txt = page.get_text('text')
            out.append(txt)
        except Exception:
            out.append(page.get_text('text'))
    doc.close()
    return '\n'.join(out)

def safe_name(s):
    return re.sub(r'[^A-Za-z0-9._-]', '_', s)[:90]

# 1) EPMC lookup for all candidates
for c in cands:
    if c.get('pmcid'):
        continue
    doi = c.get('doi')
    if not doi:
        continue
    try:
        u = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=' +
             urllib.parse.quote('DOI:' + doi) + '&format=json&resultType=core')
        raw, _ = get(u)
        res = json.loads(raw).get('resultList', {}).get('result', [])
        if res:
            r0 = res[0]
            c['pmcid'] = r0.get('pmcid')
            c['epmc_oa'] = r0.get('isOpenAccess')
            c['epmc_in_epmc'] = r0.get('inEPMC')
    except Exception as e:
        print('epmc lookup fail', doi, str(e)[:60])
    time.sleep(0.3)

json.dump(cands, open(CAND, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
n_pmc = sum(1 for c in cands if c.get('pmcid') and c.get('epmc_in_epmc') == 'Y')
print('candidates with EPMC full text:', n_pmc)

# 2) fetch full text
fetched, failed = 0, []
for c in cands:
    if not c.get('is_oa'):
        continue
    doi = c.get('doi') or c.get('openalex_id') or ''
    base = safe_name(doi.replace('https://doi.org/', ''))
    txt_path = os.path.join(FT, base + '.txt')
    c['fulltext_file'] = None
    if os.path.exists(txt_path) and os.path.getsize(txt_path) > 3000:
        c['fulltext_file'] = os.path.basename(txt_path)
        continue
    got = None
    # EPMC XML first
    if c.get('pmcid') and c.get('epmc_in_epmc') == 'Y':
        try:
            raw, _ = get('https://www.ebi.ac.uk/europepmc/webservices/rest/' + c['pmcid'] + '/fullTextXML')
            got = xml_to_text(raw)
            c['fulltext_route'] = 'epmc_xml'
        except Exception as e:
            print('xml fail', doi, str(e)[:60])
    # direct HTML
    if not got or len(got) < 3000:
        for u in filter(None, [c.get('oa_url')]):
            try:
                raw, ct = get(u, ua=UA_BROWSER)
                if 'pdf' in (ct or '') or u.lower().endswith('.pdf'):
                    tmp = os.path.join(FT, base + '.pdf')
                    open(tmp, 'wb').write(raw)
                    got = pdf_to_text(tmp)
                    os.remove(tmp)
                else:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(raw, 'lxml')
                    for bad in soup(['script', 'style', 'nav', 'header', 'footer']):
                        bad.decompose()
                    # try to keep tables
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
                    got = '\n'.join(lines)
                if got and len(got) > 3000:
                    c['fulltext_route'] = c.get('fulltext_route') or ('html:' + u.split('/')[2])
            except Exception as e:
                print('html fail', doi, u.split('/')[2] if u else '', str(e)[:50])
    # PDF route
    if not got or len(got) < 3000:
        for u in filter(None, [c.get('oa_pdf_url')]):
            try:
                raw, _ = get(u, ua=UA_BROWSER, timeout=120)
                tmp = os.path.join(FT, base + '.pdf')
                open(tmp, 'wb').write(raw)
                got = pdf_to_text(tmp)
                os.remove(tmp)
                c['fulltext_route'] = 'pdf:' + u.split('/')[2]
            except Exception as e:
                print('pdf fail', doi, str(e)[:50])
    if got and len(got) > 3000:
        header = f"SOURCE doi={doi}\nTITLE: {c.get('title')}\nYEAR: {c.get('year')}\nJOURNAL: {c.get('journal')}\nOA_URL: {c.get('oa_url')}\n\n"
        open(txt_path, 'w', encoding='utf-8').write(header + got)
        c['fulltext_file'] = os.path.basename(txt_path)
        fetched += 1
        print('OK', doi, len(got), c.get('fulltext_route'))
    else:
        failed.append(doi)
        print('NO FULLTEXT', doi, c.get('title', '')[:60])
    json.dump(cands, open(CAND, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

print('fetched:', fetched, 'failed:', len(failed))
