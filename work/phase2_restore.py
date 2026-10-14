"""Reversibility: restore every Phase-2-modified file from work/backup_phase1/.

Usage:
  python work/phase2_restore.py            # restore in place (undoes Phase 2)
  python work/phase2_restore.py <dir>      # restore into <dir> (sandbox test, leaves live files alone)
"""
import shutil, sys
from pathlib import Path

SRC = Path('work/backup_phase1')
ROOT_FILES = ['thermal_conductivity_dataset.csv', 'paper_inventory.csv', 'extraction_log.csv',
              'uncertain_measurements.csv', 'unusable_sources.csv', 'quality_control_report.md',
              'README.md']
WORK_FILES = ['rows_raw.jsonl', 'extraction_log.jsonl']

dest_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
if not SRC.is_dir():
    print(f'FATAL: {SRC} not found'); sys.exit(2)
missing = [f for f in ROOT_FILES + WORK_FILES if not (SRC / f).exists()]
if missing:
    print(f'FATAL: backup incomplete, missing: {missing}'); sys.exit(2)

for f in ROOT_FILES:
    shutil.copy2(SRC / f, dest_root / f)
    print(f'restored {dest_root / f}')
work_dest = dest_root / 'work' if len(sys.argv) > 1 else Path('work')
work_dest.mkdir(exist_ok=True)
for f in WORK_FILES:
    shutil.copy2(SRC / f, work_dest / f)
    print(f'restored {work_dest / f}')
print('RESTORE OK')
