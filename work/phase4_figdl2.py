import requests, os, time
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')
os.makedirs(FIG, exist_ok=True)
TARGETS = {
    'molecules-21-00670-g003.jpg': 'https://cdn.ncbi.nlm.nih.gov/pmc/blobs/9bdc/6273151/aed5772a1e60/molecules-21-00670-g003.jpg',
    'molecules-21-00670-g002.jpg': 'https://cdn.ncbi.nlm.nih.gov/pmc/blobs/9bdc/6273151/8ab5f4f70b6e/molecules-21-00670-g002.jpg',
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
print('figures dir now:')
for f in sorted(os.listdir(FIG)):
    print(' ', f, os.path.getsize(os.path.join(FIG, f)))
