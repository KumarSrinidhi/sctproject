import json
p = 'work/fulltext/10.1063_5.0211580.json'
t = open(p, encoding='utf-8').read()
print('rawlen', len(t), repr(t[:80]))
try:
    s = json.loads(t)
    if isinstance(s, str):
        open('work/fulltext/10.1063_5.0211580.txt', 'w', encoding='utf-8').write(s)
        print('decoded+saved txt len', len(s))
    else:
        print('not str', type(s))
except Exception as e:
    print('decode fail', e)
