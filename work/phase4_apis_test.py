import json, urllib.request, ssl, traceback
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={'User-Agent':'Mozilla/5.0 (phase4-research; mailto:phase4@example.com)'}
urls = [
 'https://api.semanticscholar.org/graph/v1/paper/DOI:10.1039/d4dt00979g?fields=title,openAccessPdf,externalIds',
 'https://api.openalex.org/works/https://doi.org/10.1039/d4dt00979g',
 'https://api.crossref.org/works/10.1039/d4dt00979g',
 'https://api.unpaywall.org/v2/10.1039/d4dt00979g?email=phase4@example.com',
]
for u in urls:
    try:
        req=urllib.request.Request(u, headers=UA)
        d=urllib.request.urlopen(req,timeout=25,context=ctx).read()
        print('OK', len(d), u[:70])
        print('   ', d[:250])
    except Exception as e:
        print('FAIL', u[:70], '->', type(e).__name__, str(e)[:150])
