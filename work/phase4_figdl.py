import requests, os, time
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(FIG, exist_ok=True)
# blobs URLs discovered via browser on PMC figure pages
TARGETS = {
    'polymers-11-01156-g011.jpg': 'https://cdn.ncbi.nlm.nih.gov/pmc/blobs/4b03/6680888/e25d57e43448/polymers-11-01156-g011.jpg',
}
for name, url in TARGETS.items():
    for attempt in range(2):
        try:
            r = requests.get(url, headers=UA, timeout=45)
            print(r.status_code, len(r.content), r.headers.get('Content-Type',''), name)
            if r.status_code == 200 and r.content[:3] == b'\xff\xd8\xff':
                with open(os.path.join(FIG, name), 'wb') as f:
                    f.write(r.content)
                print('SAVED', name, len(r.content))
            break
        except Exception as e:
            print('FAIL', type(e).__name__, str(e)[:120])
            time.sleep(2)
