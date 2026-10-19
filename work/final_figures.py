"""Final-phase figures, generated strictly from the final dataset values."""
import json, collections
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

rows = [json.loads(l) for l in open('work/rows_raw.jsonl', encoding='utf-8')]
OUT = Path('figures'); OUT.mkdir(exist_ok=True)
k = [float(r['k_composite_W_mK']) for r in rows]

# 1. k distribution histogram (log x: range spans 0.17-47)
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.hist(k, bins=30, color='#3b6fb6', edgecolor='white')
ax.set_xscale('log')
ax.set_xlabel('k composite (W/m·K, log scale)')
ax.set_ylabel('Number of measurements')
ax.set_title(f'Thermal conductivity distribution (n={len(k)}, median={sorted(k)[len(k)//2]:.2f} W/m·K)')
ax.axvline(sorted(k)[len(k)//2], color='crimson', ls='--', lw=1, label='median')
ax.legend()
fig.tight_layout(); fig.savefig(OUT/'01_k_distribution.png', dpi=150); plt.close(fig)

# 2. rows per year
years = collections.Counter(int(r['year']) for r in rows if str(r.get('year') or '').strip())
fig, ax = plt.subplots(figsize=(9, 4.2))
xs = list(range(min(years), max(years)+1))
ax.bar(xs, [years.get(y, 0) for y in xs], color='#4c9f70', edgecolor='white')
ax.set_xlabel('Publication year'); ax.set_ylabel('Rows extracted')
ax.set_title(f'Rows per year ({min(years)}–{max(years)})')
fig.tight_layout(); fig.savefig(OUT/'02_rows_per_year.png', dpi=150); plt.close(fig)

# 3. rows by filler (horizontal)
fill = collections.Counter(r['filler_material'] for r in rows).most_common()[::-1]
fig, ax = plt.subplots(figsize=(7.5, 5.2))
ax.barh([f for f, _ in fill], [c for _, c in fill], color='#b66f3b', edgecolor='white')
ax.set_xlabel('Rows'); ax.set_title(f'Rows by filler material (n={len(rows)})')
fig.tight_layout(); fig.savefig(OUT/'03_rows_by_filler.png', dpi=150); plt.close(fig)

# 4. rows by matrix
def bucket(m):
    m = (m or '').lower()
    if any(t in m for t in ('epoxy', 'dgeba', 'emc', 'etl', 'ejbn')) or m.strip() in ('ep', 'lc epoxy', 'liquid crystal epoxy'):
        return 'Epoxy-based'
    if 'silicone' in m: return 'Silicone'
    if 'polyimide' in m or m.strip() == 'pi': return 'Polyimide'
    if 'pdms' in m or 'polydimethylsiloxane' in m: return 'PDMS'
    if 'peg' in m: return 'PEG PCM'
    if 'polyurethane' in m or m.strip() == 'pu': return 'Polyurethane'
    if 'polystyrene' in m or m.strip() == 'ps': return 'Polystyrene'
    return 'Other'
mat = collections.Counter(bucket(r['matrix_polymer']) for r in rows).most_common()
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.bar([m for m, _ in mat], [c for _, c in mat], color='#704c9f', edgecolor='white')
ax.set_ylabel('Rows'); ax.set_title('Rows by matrix polymer')
for i, (_, c) in enumerate(mat):
    ax.text(i, c, str(c), ha='center', va='bottom', fontsize=9)
fig.tight_layout(); fig.savefig(OUT/'04_rows_by_matrix.png', dpi=150); plt.close(fig)

# 5. confidence + value_source breakdown (two panels)
conf = collections.Counter(r['confidence'] for r in rows)
src = collections.Counter(r['value_source'] for r in rows)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.5, 3.8))
colors = {'High': '#2e8b57', 'Medium': '#e0a030'}
ax1.bar(list(conf), list(conf.values()), color=[colors[c] for c in conf], edgecolor='white')
ax1.set_title('By confidence')
for i, v in enumerate(conf.values()):
    ax1.text(i, v, f'{v}\n({100*v/len(rows):.0f}%)', ha='center', va='bottom', fontsize=9)
src_colors = {'text': '#3b6fb6', 'table': '#b66f3b', 'figure': '#7a6fb6'}
ax2.bar(list(src), list(src.values()), color=[src_colors.get(s, '#888888') for s in src], edgecolor='white')
ax2.set_title('By value source')
for i, v in enumerate(src.values()):
    ax2.text(i, v, str(v), ha='center', va='bottom', fontsize=9)
fig.suptitle(f'Breakdown of {len(rows)} rows')
fig.tight_layout(); fig.savefig(OUT/'05_confidence_value_source.png', dpi=150); plt.close(fig)

# 6 (bonus). k vs loading scatter, colored by filler family
def fam(f):
    f = (f or '').lower()
    if f in ('h-bn', 'bn', 'bnns', 'cbn'): return 'BN family'
    if 'bn' in f: return 'BN hybrid'
    if f.startswith('aln'): return 'AlN'
    if f == 'none': return 'neat'
    return 'other ceramic'
famcolor = {'BN family': '#3b6fb6', 'BN hybrid': '#8f5fb6', 'AlN': '#b66f3b',
            'neat': '#888888', 'other ceramic': '#4c9f70'}
fig, ax = plt.subplots(figsize=(7, 4.6))
plotted = set()
for r in rows:
    load = r.get('filler_loading_wt_pct')
    if load in (None, ''): load = r.get('filler_loading_vol_pct')
    if load in (None, ''): continue
    try: x = float(load)
    except (TypeError, ValueError): continue
    f = fam(r['filler_material']); lbl = f if f not in plotted else None
    plotted.add(f)
    ax.scatter(x, float(r['k_composite_W_mK']), s=18, alpha=0.7,
               color=famcolor.get(f, '#999999'), label=lbl)
ax.set_yscale('log')
ax.set_xlabel('Filler loading (wt% or vol%, as recorded)')
ax.set_ylabel('k composite (W/m·K, log scale)')
ax.set_title('k vs filler loading, by filler family')
ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(OUT/'06_k_vs_loading.png', dpi=150); plt.close(fig)

print('figures written:', sorted(p.name for p in OUT.glob('*.png')))
