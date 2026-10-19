import requests, time, os
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
urls = [
    'https://pmc.ncbi.nlm.nih.gov/articles/PMC6680888/bin/polymers-11-01156-g011.jpg',
    'https://pmc.ncbi.nlm.nih.gov/articles/instance/6680888/bin/polymers-11-01156-g011.jpg',
    'https://www.mdpi.com/2073-4360/11/7/1156',
    'https://mdpi-res.com/d_attachment/polymers/polymers-11-01156/article_deploy/polymers-11-01156-g011.png',
]
for u in urls:
    try:
        r = requests.get(u, headers=UA, timeout=30, allow_redirects=True)
        print(r.status_code, len(r.content), r.headers.get('Content-Type', '')[:40], u[:85], '->', r.url[:90])
    except Exception as e:
        print('FAIL', type(e).__name__, str(e)[:100], u[:85])
    time.sleep(1)
