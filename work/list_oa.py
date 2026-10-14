import json
c = json.load(open(r'work\candidates.json', encoding='utf-8'))
oa = [x for x in c if x.get('is_oa')]
oa.sort(key=lambda x: x.get('year') or 0, reverse=True)
for i, x in enumerate(oa):
    j = (x.get('journal') or '')[:26]
    print(f"{i:3d} | {x.get('year')} | {j:26s} | {x.get('doi')} | {x['title'][:95]}")
print('OA total', len(oa))
