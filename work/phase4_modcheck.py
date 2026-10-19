mods = ['pypdf', 'fitz', 'pdfminer', 'requests', 'bs4', 'lxml']
for m in mods:
    try:
        mod = __import__(m)
        v = getattr(mod, '__version__', 'ok')
        print(m, v)
    except Exception as e:
        print(m, 'MISSING', type(e).__name__)
