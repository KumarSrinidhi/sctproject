import json, ssl, urllib.request, time
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (mailto:phase4@example.com)'}
dois = ['10.1016/j.compscitech.2020.108304', '10.1016/j.compscitech.2020.108322',
        '10.1002/pc.27985', '10.1016/j.jcomc.2020.100087', '10.1016/j.cej.2018.04.196',
        '10.1016/j.apsusc.2020.147091', '10.1016/j.compositesb.2020.107855',
        '10.1177/0021998320942575', '10.1177/09540083211046456',
        '10.1080/15440478.2021.1966568', '10.1002/adfm.201900412',
        '10.1002/slct.202507155', '10.1002/app.55612', '10.1002/pc.29136',
        '10.1063/5.0205196', '10.1063/1.5121349', '10.1002/smll.75841',
        '10.1002/pc.70149', '10.1088/1361-6463/ae6b9b']
out = {}
for d in dois:
    try:
        req = urllib.request.Request(f'https://api.crossref.org/works/{d}', headers=UA)
        j = json.loads(urllib.request.urlopen(req, timeout=20, context=ctx).read())
        m = j['message']
        out[d] = {'title': (m.get('title') or [''])[0], 'journal': (m.get('container-title') or [''])[0],
                  'year': (m.get('issued', {}).get('date-parts') or [[None]])[0][0]}
    except Exception as e:
        out[d] = {'err': str(e)[:80]}
    time.sleep(0.3)
json.dump(out, open('work/phase4_titles.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
for d, v in out.items():
    print(d, '|', v.get('title', v)[:110], '|', v.get('journal', '')[:40], v.get('year'))
