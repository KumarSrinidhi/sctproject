import requests, json, re, time

DOIs = [
    '10.3390/polym15051214',
    '10.3390/polym16081169',
    '10.3390/polym11071156',
    '10.3390/nano13152243',
    '10.1039/c8ra10645b',
    '10.3390/polym10030277',
    '10.3390/molecules21050670',
    '10.3390/polym17111507',
]

def fetch_epmc(doi):
    try:
        r = requests.get('https://www.ebi.ac.uk/europepmc/webservices/rest/search',
                        params={'query': f'DOI:{doi}', 'format': 'json'}, timeout=20)
        if r.status_code != 200: return None
        res = r.json().get('resultList',{}).get('result',[])
        if not res: return None
        pmcid = res[0].get('pmcid')
        if not pmcid: return None
        r2 = requests.get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML', timeout=20)
        if r2.status_code != 200: return None
        return pmcid, r2.text
    except Exception as e:
        return None

out = []
for doi in DOIs:
    got = fetch_epmc(doi)
    if got:
        pmcid, xml = got
        # strip tags crudely to text
        text = re.sub(r'<[^>]+>', ' ', xml)
        text = re.sub(r'\s+', ' ', text)
        path = rf'work\fulltext\{doi.replace("/","_")}.txt'
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f'SOURCE doi={doi} FETCH=EPMC {pmcid}\n')
            f.write(text)
        # count k hits
        hits = re.findall(r'([0-9]+\.[0-9]+)\s*(?:±\s*[0-9.]+\s*)?(?:W\s*/\s*\(?m|W\s*m\s*[\u2212–-]|W/m)', text)
        good_hits = [float(h) for h in hits if 0.05 < float(h) < 50]
        out.append({'doi': doi, 'pmcid': pmcid, 'hits': len(good_hits), 'status': 'ok'})
        print(f'{doi} {pmcid} hits={len(good_hits)}')
    else:
        out.append({'doi': doi, 'status': 'no_epmc'})
        print(f'{doi} no EPMC')
    time.sleep(0.5)

json.dump(out, open(r'work\refetch_wave1.json','w',encoding='utf-8'), indent=2)
print('done', sum(1 for o in out if o['status']=='ok'))
