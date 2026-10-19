import requests, time
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
for url in ['https://hdl.handle.net/20.500.12868/5476', 'https://revistas.ucp.edu.ec/index.php/ptec/article/view/5476']:
    for attempt in range(2):
        try:
            r = requests.get(url, headers=UA, timeout=30, allow_redirects=True)
            print('OK', r.status_code, url, '->', r.url, 'len', len(r.content))
            open('work/tmp_page.html','wb').write(r.content)
            break
        except Exception as e:
            print('FAIL', type(e).__name__, str(e)[:120], url)
            time.sleep(2)
