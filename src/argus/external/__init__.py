"""External datasets: harmonize, cross-check against ARGUS, and use as an independent test set.

External data never enters data/records/. It is read from data/external/<source>/,
mapped onto the ARGUS 31-column row so the same enrichment, vocabulary and
features apply, and kept apart in every analysis.
"""
