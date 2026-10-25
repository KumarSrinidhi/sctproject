"""Phase 6, acquisition: find, screen and fetch new open-access papers.

discovery  openalex.py   OpenAlex search (API key), every query logged
screening  screen.py     title/abstract rules, every decision with a reason code
full text  europepmc.py  Europe PMC JATS XML, licence recorded, cached in sources/
checking   quotes.py     every extracted value's quote must occur in its source

Nothing here writes data/records/: new records are created only after each
value has been checked against its source.
"""
