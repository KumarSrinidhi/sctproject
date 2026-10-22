"""ARGUS: source-verified thermal conductivity data for polymer-ceramic composites.

Layers (see docs/ARCHITECTURE.md):
    records   - curated per-paper YAML files, the source of truth
    validate  - rule-based checks that block bad rows
    build     - compiles records into the published CSV deliverables
    enrich    - controlled vocabularies, unit and loading conversion
    physics   - effective-medium models for composite conductivity
    verify    - end-state invariants written to a verification report
"""

__version__ = "0.3.0"
