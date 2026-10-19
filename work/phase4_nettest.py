import os, json, time, urllib.request, ssl, socket

# network smoke test: EPMC DOI search, unpaywall
ctx = ssl.create_default_context()

def get(url, timeout=30, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0 (research-curation)'} )
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.read()

tests = [
    'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%2210.1039/d4dt00979g%22&format=json',
    'https://api.unpaywall.org/v2/10.1016/j.cej.2018.04.196?email=research@example.org',
]
for u in tests:
    try:
        status, body = get(u)
        print('OK', status, u[:70], 'len', len(body))
        print('   ', body[:200])
    except Exception as e:
        print('FAIL', type(e).__name__, e, u[:70])
