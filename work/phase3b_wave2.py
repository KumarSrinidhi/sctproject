import os, re, time, urllib.request, json

BASE = os.path.dirname(os.path.abspath(__file__))
FT = os.path.join(BASE, 'fulltext')
UA_BROWSER = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36')
CAPTCHA = ('radware', 'captcha', 'enable javascript', 'access denied', 'request unsuccessful')


def get(url, timeout=60, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA_BROWSER, 'Accept': '*/*'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), r.headers.get('Content-Type', '')
        except Exception as e:
            last = e
            time.sleep(2 + 3 * i)
    raise last


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


def html_to_text(raw):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(raw, 'lxml')
    for bad in soup(['script', 'style', 'nav', 'header', 'footer']):
        bad.decompose()
    lines = []
    for el in soup.find_all(['h1', 'h2', 'h3', 'p', 'table', 'figcaption']):
        if el.name == 'table':
            lines.append('[TABLE]')
            for tr in el.find_all('tr'):
                lines.append(' | '.join(c.get_text(' ', strip=True) for c in tr.find_all(['td', 'th'])))
            lines.append('[/TABLE]')
        elif el.name == 'figcaption':
            lines.append('[FIG] ' + el.get_text(' ', strip=True))
        else:
            lines.append(el.get_text(' ', strip=True))
    return '\n'.join(lines)


def slug(doi):
    return re.sub(r'[^A-Za-z0-9._-]', '_', doi)[:90]


def find_pdf_links(raw, base_url):
    from bs4 import BeautifulSoup
    from urllib.parse import urljoin
    soup = BeautifulSoup(raw, 'lxml')
    out = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if '.pdf' in href.lower():
            out.append(urljoin(base_url, href))
    return out[:5]


TARGETS = [
    # (doi, title, year, journal, [urls])
    ('10.1002/pc.29136',
     'Enhancing directional thermal conductivity in hexagonal boron nitride reinforced epoxy composites',
     2024, 'Polymer Composites',
     ['https://hdl.handle.net/20.500.12868/5476']),
    ('10.1007/s10854-024-13657-3',
     'Functionalization of boron nitride with poly(catechol-polyamine) and bis(gamma-triethoxysilylpropyl)disulfide',
     2024, 'Journal of Materials Science: Materials in Electronics',
     ['https://link.springer.com/content/pdf/10.1007/s10854-024-13657-3.pdf']),
]

log = []
for doi, title, year, journal, urls in TARGETS:
    path = os.path.join(FT, slug(doi) + '.txt')
    if os.path.exists(path) and os.path.getsize(path) > 3000:
        print('exists', doi); continue
    saved = False
    for u in urls:
        try:
            raw, ct = get(u)
            if 'pdf' in (ct or '') or u.lower().endswith('.pdf') or raw[:4] == b'%PDF':
                tmp = os.path.join(FT, slug(doi) + '.tmp.pdf')
                open(tmp, 'wb').write(raw)
                body = pdf_to_text(tmp)
                os.remove(tmp)
            else:
                txt = raw.decode('utf-8', 'replace')
                if any(c in txt[:6000].lower() for c in CAPTCHA):
                    print('blocked page', doi, u); continue
                pdfs = find_pdf_links(raw, u)
                if pdfs:
                    for pu in pdfs:
                        try:
                            praw, pct = get(pu)
                            if praw[:4] == b'%PDF' or 'pdf' in (pct or ''):
                                tmp = os.path.join(FT, slug(doi) + '.tmp.pdf')
                                open(tmp, 'wb').write(praw)
                                body = pdf_to_text(tmp)
                                os.remove(tmp)
                                header = ('SOURCE doi=%s FETCH=%s\nTITLE: %s\nYEAR: %s\nJOURNAL: %s\n\n'
                                          % (doi, pu.split('/')[2], title, year, journal))
                                open(path, 'w', encoding='utf-8').write(header + body)
                                print('SAVED', doi, len(body), pu)
                                log.append(dict(doi=doi, url=pu, outcome='saved', chars=len(body)))
                                saved = True
                                break
                        except Exception as e:
                            print('fail pdf', doi, pu, str(e)[:80])
                    if saved:
                        break
                body = html_to_text(raw)
            if body and len(body) > 3000:
                header = ('SOURCE doi=%s FETCH=%s\nTITLE: %s\nYEAR: %s\nJOURNAL: %s\n\n'
                          % (doi, u.split('/')[2], title, year, journal))
                open(path, 'w', encoding='utf-8').write(header + body)
                print('SAVED', doi, len(body), u)
                log.append(dict(doi=doi, url=u, outcome='saved', chars=len(body)))
                saved = True
                break
            else:
                print('short', doi, u, len(body or ''))
        except Exception as e:
            print('fail', doi, u, str(e)[:100])
            log.append(dict(doi=doi, url=u, outcome='fail', note=str(e)[:150]))
    if not saved and not any(e['doi'] == doi for e in log):
        log.append(dict(doi=doi, outcome='no_route'))

json.dump(log, open(os.path.join(BASE, 'phase3b_wave2_log.json'), 'w', encoding='utf-8'), indent=1)
print('wave2 done', log)
