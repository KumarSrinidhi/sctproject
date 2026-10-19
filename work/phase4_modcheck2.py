mods = ['playwright', 'websocket', 'websockets', 'pychrome', 'requests']
for m in mods:
    try:
        mod = __import__(m)
        print(m, getattr(mod, '__version__', 'ok'))
    except Exception as e:
        print(m, 'MISSING')
