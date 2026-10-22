(function () {
  "use strict";

  // ------------------------------------------------------------------ data
  const DATA = JSON.parse(document.getElementById("argus-data").textContent);
  const ROWS = DATA.rows;
  const META = DATA.meta;
  const CURVES = DATA.curves;
  const BY_ID = {};
  ROWS.forEach((r) => {
    r.mfg = r.mf === "epoxy" ? "epoxy" : "other";
    r.deg = ["through-plane", "in-plane", "mixed"].includes(r.de) ? r.de : "unknown";
    BY_ID[r.id] = r;
  });

  const SVGNS = "http://www.w3.org/2000/svg";
  const $ = (sel) => document.querySelector(sel);

  function el(tag, attrs, text) {
    const e = document.createElement(tag);
    if (attrs) for (const k in attrs) {
      if (k === "class") e.className = attrs[k];
      else e.setAttribute(k, attrs[k]);
    }
    if (text !== undefined && text !== null) e.textContent = text;
    return e;
  }
  function sv(tag, attrs) {
    const e = document.createElementNS(SVGNS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  const num = (v) => (v === null || v === undefined ? "—" : String(Number(Number(v).toPrecision(4))));
  const median = (a) => {
    if (!a.length) return null;
    const s = a.slice().sort((x, y) => x - y);
    const m = Math.floor(s.length / 2);
    return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
  };
  const sci = (x) => {
    const e = Math.floor(Math.log10(Math.abs(x)));
    const sup = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };
    return (x / Math.pow(10, e)).toFixed(1) + "×10" + String(e).split("").map((c) => sup[c]).join("");
  };

  // ------------------------------------------------------------------ vocabularies
  const METHOD_LABEL = {
    LFA: "Laser flash", TPS: "Hot Disk / TPS", THB: "Transient hot bridge", HOT_WIRE: "Hot wire",
    MTPS: "Modified TPS", SS_D5470: "Steady state (D5470-type)", SS_GHFM: "Guarded heat flow",
    SS_HFM_GHP: "Heat flow meter", SS_UNSPECIFIED: "Steady state", PERIODIC: "Periodic heating",
    THIN_FILM: "Thin-film method", IR_THERMO: "IR thermography", UNSPECIFIED: "Not stated",
  };
  const FLAG_LABEL = {
    mixed_direction_anisotropic: "mixed direction on platelets",
    contact_resistance_included: "contact resistance included",
    lfa_cp_rho_unreported: "Cp and density source not stated",
    method_unspecified: "technique not stated",
    abstract_only: "abstract only",
    figure_digitized: "digitized from a figure",
    matrix_prefilled: "matrix already filled",
    co_filler_ignored_in_conversion: "co-filler ignored in vol%",
    non_ambient_temperature: "non-ambient temperature",
  };
  const BASIS_LABEL = {
    reported: "reported", "converted-from-wt": "converted from wt%", "converted-from-vol": "converted from vol%",
    "method-default": "assumed from the technique", "method-text": "from the method description",
    "reference-default": "family default, not reported", none: "not known",
  };
  const PV_LABEL = { fulltext: "Full text", abstract: "Abstract only", figure: "Digitized figure" };

  const FILTERS = [
    { key: "fg", label: "Filler", options: [["hBN", "h-BN / BN"], ["BNNS", "BN nanosheets"], ["AlN", "AlN"], ["oxide", "Oxides, cBN"], ["hybrid", "Hybrids"], ["neat", "Neat matrix"]] },
    { key: "mfg", label: "Matrix", options: [["epoxy", "Epoxy"], ["other", "Other polymers"]] },
    { key: "mg", label: "Technique", options: [["LFA", "Laser flash"], ["TPS", "Hot Disk / TPS"], ["THB", "Hot bridge"], ["HOT_WIRE", "Hot wire"], ["STEADY", "Steady state"], ["OTHER", "Other"], ["UNSPECIFIED", "Not stated"]] },
    { key: "deg", label: "Direction", options: [["through-plane", "Through-plane"], ["in-plane", "In-plane"], ["mixed", "Mixed"], ["unknown", "Unknown"]] },
    { key: "pv", label: "Source", options: [["fulltext", "Full text"], ["abstract", "Abstract only"], ["figure", "Digitized figure"]] },
  ];

  // Three groups per view: the validated palette is colour-blind safe for three
  // series on a scatter. Colour follows the group, never the filter result.
  const COLOR_BY = {
    filler: { label: "Filler", groups: [
      ["h-BN / BN platelets", (r) => r.fg === "hBN"], ["BN nanosheets", (r) => r.fg === "BNNS"], ["Other fillers", () => true]] },
    technique: { label: "Technique", groups: [
      ["Laser flash (through-plane)", (r) => r.mg === "LFA"],
      ["Hot Disk, hot bridge, hot wire (mixed direction)", (r) => ["TPS", "THB", "HOT_WIRE"].includes(r.mg)],
      ["Steady state, other or not stated", () => true]] },
    direction: { label: "Direction", groups: [
      ["Through-plane", (r) => r.de === "through-plane"], ["In-plane", (r) => r.de === "in-plane"], ["Mixed or unknown", () => true]] },
    source: { label: "Source", groups: [
      ["Printed in the full text", (r) => r.pv === "fulltext"], ["Abstract only", (r) => r.pv === "abstract"], ["Digitized from a figure", () => true]] },
  };
  const SERIES = ["var(--s1)", "var(--s2)", "var(--s3)"];

  const YMODE = {
    k: { label: "k", axis: "k (W/m·K)", min: 0.1, max: 60, ticks: [0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50], get: (r) => r.k, scale: META.km_ref },
    en: { label: "k ÷ k matrix", axis: "k / k matrix", min: 0.8, max: 300, ticks: [1, 2, 5, 10, 20, 50, 100, 200], get: (r) => r.en, scale: 1 },
  };
  const X = { min: 0, max: 82, ticks: [0, 10, 20, 30, 40, 50, 60, 70, 80] };

  // ------------------------------------------------------------------ state
  const state = { on: {}, q: "", colorBy: "filler", y: "k", models: true, sort: { key: "k", dir: -1 }, pinned: null };
  FILTERS.forEach((f) => { state.on[f.key] = new Set(f.options.map((o) => o[0])); });
  let lastVisible = ROWS;
  let points = [];

  function groupOf(r) {
    const g = COLOR_BY[state.colorBy].groups;
    for (let i = 0; i < g.length; i++) if (g[i][1](r)) return i;
    return g.length - 1;
  }

  function visibleRows() {
    const q = state.q.trim().toLowerCase();
    return ROWS.filter((r) => FILTERS.every((f) => state.on[f.key].has(r[f.key])) &&
      (!q || [r.p, r.id, r.doi, r.t, r.mat, r.fo, r.fil, r.mm, r.sl].some((s) => s && String(s).toLowerCase().includes(q))));
  }

  // ------------------------------------------------------------------ controls
  function buildFilters() {
    const bar = $("#filters");
    const anchor = bar.firstElementChild;
    FILTERS.forEach((f) => {
      const g = el("div", { class: "fgroup", role: "group", "aria-label": f.label });
      g.appendChild(el("span", null, f.label));
      const chips = el("div", { class: "chips" });
      f.options.forEach(([value, label]) => {
        const n = ROWS.filter((r) => r[f.key] === value).length;
        if (!n) return;
        const b = el("button", { class: "chip", type: "button", "aria-pressed": "true", "data-key": f.key, "data-value": value });
        b.appendChild(document.createTextNode(label));
        b.appendChild(el("span", { class: "n" }, String(n)));
        b.addEventListener("click", () => {
          const set = state.on[f.key];
          if (set.has(value)) set.delete(value); else set.add(value);
          b.setAttribute("aria-pressed", set.has(value) ? "true" : "false");
          render();
        });
        chips.appendChild(b);
      });
      g.appendChild(chips);
      bar.insertBefore(g, anchor);
    });
    let t = null;
    $("#q").addEventListener("input", (e) => {
      clearTimeout(t);
      t = setTimeout(() => { state.q = e.target.value; render(); }, 120);
    });
    $("#reset").addEventListener("click", () => {
      FILTERS.forEach((f) => { state.on[f.key] = new Set(f.options.map((o) => o[0])); });
      document.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", "true"));
      state.q = "";
      $("#q").value = "";
      render();
    });
  }

  function buildSeg(container, options, current, onPick) {
    const box = $(container);
    box.textContent = "";
    options.forEach(([value, label]) => {
      const b = el("button", { type: "button", "aria-pressed": String(value === current) }, label);
      b.addEventListener("click", () => {
        box.querySelectorAll("button").forEach((x) => x.setAttribute("aria-pressed", "false"));
        b.setAttribute("aria-pressed", "true");
        onPick(value);
      });
      box.appendChild(b);
    });
  }

  // ------------------------------------------------------------------ summary
  function tile(label, value, sub) {
    const t = el("div", { class: "card tile" });
    t.appendChild(el("span", { class: "label" }, label));
    t.appendChild(el("span", { class: "value" }, value));
    if (sub) t.appendChild(el("span", { class: "sub" }, sub));
    return t;
  }
  function renderSummary(vis, plotted) {
    const box = $("#summary");
    box.textContent = "";
    const ks = vis.map((r) => r.k);
    const papers = new Set(vis.map((r) => r.p)).size;
    box.appendChild(tile("Measurements shown", String(vis.length), "of " + ROWS.length));
    box.appendChild(tile("Papers", String(papers), "of " + META.papers));
    box.appendChild(tile("Median k", ks.length ? num(median(ks)) + " W/m·K" : "—",
      ks.length ? "range " + num(Math.min(...ks)) + " – " + num(Math.max(...ks)) : ""));
    box.appendChild(tile("Plotted", String(plotted), "with a known volume fraction"));
  }

  // ------------------------------------------------------------------ chart
  const M = { t: 12, r: 14, b: 44, l: 54 };
  let geom = null;

  function renderChart(vis) {
    const svg = $("#chart");
    const W = Math.max(280, Math.round(svg.getBoundingClientRect().width || svg.parentNode.clientWidth - 28));
    const H = W < 560 ? 330 : 430;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("height", String(H));
    svg.textContent = "";
    const Y = YMODE[state.y];
    const lmin = Math.log10(Y.min), lmax = Math.log10(Y.max);
    const sx = (v) => M.l + ((Math.min(Math.max(v, X.min), X.max) - X.min) / (X.max - X.min)) * (W - M.l - M.r);
    const sy = (v) => M.t + (1 - (Math.log10(Math.min(Math.max(v, Y.min), Y.max)) - lmin) / (lmax - lmin)) * (H - M.t - M.b);
    geom = { W, H, sx, sy };

    const grid = sv("g", {});
    Y.ticks.forEach((t) => {
      const y = sy(t);
      grid.appendChild(sv("line", { x1: M.l, x2: W - M.r, y1: y, y2: y, stroke: "var(--grid)", "stroke-width": 1 }));
      const lab = sv("text", { x: M.l - 8, y: y + 4, "text-anchor": "end", fill: "var(--tick)", "font-size": 11 });
      lab.textContent = String(t);
      grid.appendChild(lab);
    });
    X.ticks.forEach((t) => {
      const x = sx(t);
      grid.appendChild(sv("line", { x1: x, x2: x, y1: M.t, y2: H - M.b, stroke: "var(--grid)", "stroke-width": 1 }));
      const lab = sv("text", { x: x, y: H - M.b + 16, "text-anchor": "middle", fill: "var(--tick)", "font-size": 11 });
      lab.textContent = String(t);
      grid.appendChild(lab);
    });
    grid.appendChild(sv("line", { x1: M.l, x2: W - M.r, y1: H - M.b, y2: H - M.b, stroke: "var(--axis)", "stroke-width": 1 }));
    grid.appendChild(sv("line", { x1: M.l, x2: M.l, y1: M.t, y2: H - M.b, stroke: "var(--axis)", "stroke-width": 1 }));
    const xt = sv("text", { x: M.l + (W - M.l - M.r) / 2, y: H - 8, "text-anchor": "middle", fill: "var(--ink-2)", "font-size": 12 });
    xt.textContent = "filler loading (vol%)";
    const yt = sv("text", { x: 14, y: M.t + (H - M.t - M.b) / 2, "text-anchor": "middle", fill: "var(--ink-2)", "font-size": 12,
      transform: "rotate(-90 14 " + (M.t + (H - M.t - M.b) / 2) + ")" });
    yt.textContent = Y.axis;
    grid.appendChild(xt);
    grid.appendChild(yt);
    svg.appendChild(grid);

    if (state.models) {
      const curves = [["ceiling", "3 3"], ["nan0", ""], ["nanr", "8 3"]];
      curves.forEach(([key, dash]) => {
        let d = "";
        CURVES.phi.forEach((p, i) => {
          const v = CURVES[key][i];
          if (v === null) return;
          const val = v * Y.scale;
          if (val < Y.min * 0.999 || val > Y.max * 1.001) return;
          d += (d ? "L" : "M") + sx(p).toFixed(1) + " " + sy(val).toFixed(1);
        });
        if (!d) return;
        const attrs = { d: d, fill: "none", stroke: "var(--ink-2)", "stroke-width": 1.5, "stroke-linecap": "round", "stroke-linejoin": "round" };
        if (dash) attrs["stroke-dasharray"] = dash;
        svg.appendChild(sv("path", attrs));
      });
    }

    points = [];
    const layer = sv("g", {});
    const plotted = vis.filter((r) => r.phi !== null && Y.get(r) !== null && Y.get(r) !== undefined);
    // draw slot 3 first so the two named groups sit on top
    plotted.slice().sort((a, b) => groupOf(b) - groupOf(a)).forEach((r) => {
      const x = sx(r.phi), y = sy(Y.get(r)), g = groupOf(r);
      layer.appendChild(sv("circle", { cx: x.toFixed(1), cy: y.toFixed(1), r: 4.5, fill: SERIES[g], stroke: "var(--surface)", "stroke-width": 2 }));
      points.push({ r, x, y });
    });
    svg.appendChild(layer);

    const pin = BY_ID[state.pinned];
    if (pin && plotted.includes(pin)) {
      svg.appendChild(sv("circle", { cx: sx(pin.phi), cy: sy(Y.get(pin)), r: 8, fill: "none", stroke: "var(--ink)", "stroke-width": 2 }));
    }
    svg.appendChild(sv("circle", { id: "hover-ring", cx: -20, cy: -20, r: 7, fill: "none", stroke: "var(--ink)", "stroke-width": 1.5, opacity: 0 }));

    $("#chart-empty").hidden = plotted.length > 0;
    const desc = "Scatter of " + (state.y === "k" ? "thermal conductivity" : "enhancement over the matrix") +
      " against filler loading for " + plotted.length + " measurements, coloured by " + COLOR_BY[state.colorBy].label.toLowerCase() +
      ". The table below lists every value.";
    $("#chart-desc").textContent = desc;
    renderLegend(plotted);
    const notPlotted = vis.length - plotted.length;
    $("#chart-note").textContent = (notPlotted ? notPlotted + " shown measurement" + (notPlotted > 1 ? "s have" : " has") +
      " no volume fraction (hybrid fillers or loading not convertible) and appear only in the table. " : "") +
      (state.models ? "Reference curves are for randomly oriented h-BN platelets in epoxy (k matrix " + META.km_ref + " W/m·K)." : "");
    return plotted.length;
  }

  function renderLegend(plotted) {
    const box = $("#legend");
    box.textContent = "";
    COLOR_BY[state.colorBy].groups.forEach(([label], i) => {
      const n = plotted.filter((r) => groupOf(r) === i).length;
      const k = el("span", { class: "key" });
      const d = el("span", { class: "dot" });
      d.style.background = SERIES[i];
      k.appendChild(d);
      k.appendChild(document.createTextNode(label + " "));
      k.appendChild(el("span", { class: "n" }, String(n)));
      box.appendChild(k);
    });
    if (state.models) {
      [["3 3", "Maxwell ceiling (isolated spheres, filler k → ∞)"], ["", "Nan 1997, perfect interfaces"],
        ["8 3", "Nan 1997, R_K = " + sci(META.rk_median) + " m²K/W (median fit)"]].forEach(([dash, label]) => {
        const k = el("span", { class: "key" });
        const s = document.createElementNS(SVGNS, "svg");
        s.setAttribute("width", "22");
        s.setAttribute("height", "10");
        s.setAttribute("aria-hidden", "true");
        const ln = sv("line", { x1: 1, x2: 21, y1: 5, y2: 5, stroke: "var(--ink-2)", "stroke-width": 1.5 });
        if (dash) ln.setAttribute("stroke-dasharray", dash);
        s.appendChild(ln);
        k.appendChild(s);
        k.appendChild(document.createTextNode(label));
        box.appendChild(k);
      });
    }
  }

  function nearest(evt) {
    const svg = $("#chart");
    const rect = svg.getBoundingClientRect();
    const scale = geom ? geom.W / rect.width : 1;
    const x = (evt.clientX - rect.left) * scale, y = (evt.clientY - rect.top) * scale;
    let best = null, bd = 24 * 24;
    for (const p of points) {
      const d = (p.x - x) * (p.x - x) + (p.y - y) * (p.y - y);
      if (d < bd) { bd = d; best = p; }
    }
    return best;
  }

  function showTip(p) {
    const tip = $("#tip");
    const ring = $("#hover-ring");
    if (!p) {
      tip.hidden = true;
      if (ring) ring.setAttribute("opacity", "0");
      return;
    }
    const r = p.r;
    tip.textContent = "";
    const head = state.y === "k" ? "k = " + num(r.k) + " W/m·K" : num(r.en) + "× the matrix";
    tip.appendChild(el("strong", null, head));
    tip.appendChild(el("span", { class: "m" }, r.phi.toFixed(1) + " vol% " + r.fil + " in " + r.mat));
    tip.appendChild(el("span", { class: "m" }, (METHOD_LABEL[r.mc] || r.mc) + " · " + r.de));
    const src = r.sl.length > 96 ? r.sl.slice(0, 95) + "…" : r.sl;
    tip.appendChild(el("span", { class: "s" }, r.p + " · " + r.y + " · " + src));
    tip.hidden = false;
    if (ring) {
      ring.setAttribute("cx", p.x);
      ring.setAttribute("cy", p.y);
      ring.setAttribute("opacity", "1");
    }
    const card = tip.parentNode;
    const svg = $("#chart");
    const rect = svg.getBoundingClientRect();
    const crect = card.getBoundingClientRect();
    const px = rect.left - crect.left + p.x * (rect.width / geom.W);
    const py = rect.top - crect.top + p.y * (rect.width / geom.W);
    const tw = tip.offsetWidth, th = tip.offsetHeight;
    let left = px + 14, top = py - th - 10;
    if (left + tw > crect.width - 8) left = px - tw - 14;
    if (left < 8) left = 8;
    if (top < 8) top = py + 14;
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  }

  // ------------------------------------------------------------------ detail
  function fact(dl, label, value) {
    if (value === null || value === undefined || value === "") return;
    dl.appendChild(el("dt", null, label));
    dl.appendChild(el("dd", null, value));
  }

  async function copyText(text, statusEl, ok) {
    try {
      await navigator.clipboard.writeText(text);
      statusEl.textContent = ok;
      return true;
    } catch (e) {
      statusEl.textContent = "Copying is blocked here. Select the text and copy it.";
      return false;
    }
  }

  function renderDetail() {
    const box = $("#detail");
    box.textContent = "";
    const r = BY_ID[state.pinned];
    if (!r) {
      box.appendChild(el("p", { class: "note" }, "Select a point or a table row to see the measurement and its source."));
      return;
    }
    const eb = el("p", { class: "eyebrow" }, "Selected measurement · ");
    eb.appendChild(el("span", { class: "raw mono" }, r.id));
    box.appendChild(eb);
    const big = el("div", { class: "big" });
    big.appendChild(document.createTextNode(num(r.k) + " "));
    big.appendChild(el("small", null, "W/m·K"));
    box.appendChild(big);
    if (r.en !== null) {
      box.appendChild(el("div", { class: "enh" }, r.en.toFixed(1) + "× the matrix (matrix k " + num(r.km) + " W/m·K, " +
        (BASIS_LABEL[r.kb] || r.kb) + ")"));
    }
    const dl = el("dl", { class: "facts" });
    const load = [];
    if (r.phi !== null) load.push(r.phi.toFixed(1) + " vol% (" + (BASIS_LABEL[r.pb] || r.pb) + ")");
    if (r.w !== null) load.push(num(r.w) + " wt%");
    if (!load.length && r.lo) load.push(r.lo + " " + r.lu);
    fact(dl, "Loading", load.join(" · "));
    fact(dl, "Filler", r.fo || r.fil);
    fact(dl, "Shape", [r.sh, r.sz !== null ? num(r.sz) + " µm" : "", r.al].filter(Boolean).join(" · "));
    fact(dl, "Treatment", r.fn);
    fact(dl, "Matrix", r.mat + (r.cur ? " · " + r.cur : ""));
    fact(dl, "Processing", r.pr);
    fact(dl, "Technique", r.mc === "UNSPECIFIED" ? (r.mm || "Not stated") : (METHOD_LABEL[r.mc] || r.mc) + (r.mm ? " — " + r.mm : ""));
    fact(dl, "Direction", r.de + " (" + (BASIS_LABEL[r.db] || r.db) + ")" + (r.kd && r.kd !== "unknown" && r.kd !== r.de ? "; paper says “" + r.kd + "”" : ""));
    fact(dl, "Temperature", r.T !== null ? num(r.T) + " °C" : "ambient (not stated)");
    fact(dl, "Value from", r.vs + " · " + r.cf + " confidence");
    box.appendChild(dl);
    box.appendChild(el("blockquote", { class: "quote" }, r.sl));
    if (r.nt) box.appendChild(el("p", { class: "note" }, r.nt));
    if (r.fl.length) {
      const fl = el("div", { class: "flags", "aria-label": "Caveats" });
      r.fl.forEach((f) => fl.appendChild(el("span", { class: "flag" }, FLAG_LABEL[f] || f)));
      box.appendChild(fl);
    }
    const paper = el("div", { class: "paper" });
    paper.appendChild(el("span", { class: "ttl" }, r.t));
    const line = el("span");
    line.appendChild(document.createTextNode(r.p + " · " + r.y + " · "));
    if (/^10\.\d{4,9}\/\S+$/.test(r.doi)) {
      const a = el("a", { href: "https://doi.org/" + r.doi, target: "_blank", rel: "noopener noreferrer" }, "doi:" + r.doi);
      line.appendChild(a);
    } else {
      line.appendChild(document.createTextNode(r.doi));
    }
    paper.appendChild(line);
    box.appendChild(paper);
    const actions = el("div", { class: "row-actions" });
    const btn = el("button", { class: "btn", type: "button" }, "Copy citation");
    const status = el("span", { class: "status", role: "status" });
    btn.addEventListener("click", () => {
      copyText(r.id + ", doi:" + r.doi + ", " + r.sl, status, "Copied row id, DOI and source.");
    });
    actions.appendChild(btn);
    actions.appendChild(status);
    box.appendChild(actions);
  }

  // ------------------------------------------------------------------ table
  const COLS = [
    { key: "k", label: "k (W/m·K)", num: true, get: (r) => r.k },
    { key: "en", label: "× matrix", num: true, get: (r) => r.en, fmt: (r) => (r.en === null ? "—" : r.en.toFixed(1)) },
    { key: "phi", label: "vol%", num: true, get: (r) => r.phi, fmt: (r) => (r.phi === null ? "—" : r.phi.toFixed(1) + (r.pb === "converted-from-wt" ? "*" : "")) },
    { key: "w", label: "wt%", num: true, get: (r) => r.w, fmt: (r) => num(r.w) },
    { key: "fil", label: "Filler", get: (r) => r.fil },
    { key: "mat", label: "Matrix", get: (r) => r.mat, wrap: true },
    { key: "mc", label: "Technique", get: (r) => METHOD_LABEL[r.mc] || r.mc },
    { key: "de", label: "Direction", get: (r) => r.de },
    { key: "pv", label: "Source", get: (r) => PV_LABEL[r.pv] },
    { key: "p", label: "Paper", get: (r) => r.p + " · " + r.y },
  ];

  function buildHead() {
    const tr = $("#thead");
    tr.textContent = "";
    COLS.forEach((c) => {
      const th = el("th", { scope: "col", class: c.num ? "num" : "" });
      if (state.sort.key === c.key) th.setAttribute("aria-sort", state.sort.dir > 0 ? "ascending" : "descending");
      const b = el("button", { type: "button" }, c.label);
      b.addEventListener("click", () => {
        if (state.sort.key === c.key) state.sort.dir *= -1;
        else state.sort = { key: c.key, dir: c.num ? -1 : 1 };
        buildHead();
        renderTable(lastVisible);
      });
      th.appendChild(b);
      tr.appendChild(th);
    });
  }

  function sorted(vis) {
    const c = COLS.find((x) => x.key === state.sort.key);
    const d = state.sort.dir;
    return vis.slice().sort((a, b) => {
      const va = c.get(a), vb = c.get(b);
      if (va === null || va === undefined) return 1;
      if (vb === null || vb === undefined) return -1;
      if (c.num) return (va - vb) * d;
      return String(va).localeCompare(String(vb)) * d;
    });
  }

  function renderTable(vis) {
    const body = $("#tbody");
    body.textContent = "";
    if (!vis.length) {
      const tr = el("tr");
      const td = el("td", { colspan: String(COLS.length) }, "No measurements match these filters. ");
      const b = el("button", { class: "btn", type: "button" }, "Reset filters");
      b.addEventListener("click", () => $("#reset").click());
      td.appendChild(b);
      tr.appendChild(td);
      body.appendChild(tr);
      return;
    }
    sorted(vis).forEach((r) => {
      const tr = el("tr", { "data-id": r.id });
      if (r.id === state.pinned) tr.className = "pinned";
      COLS.forEach((c, i) => {
        const td = el("td", { class: (c.num ? "num" : "") + (c.wrap ? " wrap" : "") });
        if (i === 0) {
          const sw = el("span", { class: "swatch", "aria-hidden": "true" });
          sw.style.background = SERIES[groupOf(r)];
          td.appendChild(sw);
          const b = el("button", { class: "kbtn", type: "button", "aria-label": "Show details for " + num(r.k) + " W/m·K, " + r.p + ", row " + r.id }, num(r.k));
          td.appendChild(b);
        } else {
          td.textContent = c.fmt ? c.fmt(r) : (c.get(r) === null || c.get(r) === undefined ? "—" : String(c.get(r)));
        }
        tr.appendChild(td);
      });
      tr.addEventListener("click", (e) => {
        if (e.target.closest("a")) return;
        pin(r.id);
      });
      body.appendChild(tr);
    });
  }

  function csvCell(v) {
    const s = v === null || v === undefined ? "" : String(v);
    return /[",\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }
  function csvOf(vis) {
    const head = ["row_id", "paper_id", "doi", "year", "filler_material", "matrix_polymer", "phi_vol_pct", "phi_basis",
      "filler_loading_wt_pct", "k_composite_W_mK", "k_matrix_effective", "method_class", "measurement_method",
      "direction_reported", "direction_effective", "value_source", "confidence", "source_location"];
    const lines = [head.join(",")];
    sorted(vis).forEach((r) => {
      lines.push([r.id, r.p, r.doi, r.y, r.fil, r.mat, r.phi, r.pb, r.w, r.k, r.km, r.mc, r.mm, r.dr, r.de, r.vs, r.cf, r.sl]
        .map(csvCell).join(","));
    });
    return lines.join("\n");
  }

  // ------------------------------------------------------------------ orchestration
  function pin(id) {
    state.pinned = id;
    renderDetail();
    document.querySelectorAll("#tbody tr").forEach((tr) => {
      tr.classList.toggle("pinned", tr.getAttribute("data-id") === id);
    });
    renderChart(lastVisible);
  }

  function render() {
    lastVisible = visibleRows();
    if (state.pinned && !lastVisible.includes(BY_ID[state.pinned])) state.pinned = lastVisible.length ? sorted(lastVisible)[0].id : null;
    const plotted = renderChart(lastVisible);
    renderSummary(lastVisible, plotted);
    renderTable(lastVisible);
    renderDetail();
    $("#table-title").textContent = "Measurements (" + lastVisible.length + ")";
  }

  function init() {
    buildFilters();
    buildSeg("#colorby", Object.keys(COLOR_BY).map((k) => [k, COLOR_BY[k].label]), state.colorBy, (v) => { state.colorBy = v; render(); });
    buildSeg("#ymode", Object.keys(YMODE).map((k) => [k, YMODE[k].label]), state.y, (v) => { state.y = v; renderChart(lastVisible); showTip(null); });
    $("#models").addEventListener("change", (e) => { state.models = e.target.checked; renderChart(lastVisible); });
    buildHead();
    const svg = $("#chart");
    svg.addEventListener("pointermove", (e) => showTip(nearest(e)));
    svg.addEventListener("pointerleave", () => showTip(null));
    svg.addEventListener("click", (e) => {
      const p = nearest(e);
      if (p) pin(p.r.id);
    });
    $("#copy-csv").addEventListener("click", async () => {
      const text = csvOf(lastVisible);
      const ok = await copyText(text, $("#copy-status"), "Copied " + lastVisible.length + " rows as CSV.");
      const fb = $("#csv-fallback");
      fb.hidden = ok;
      if (!ok) {
        fb.value = text;
        fb.focus();
        fb.select();
      }
    });
    // open on the highest-k High-confidence measurement that is plotted
    const firm = sorted(ROWS).filter((r) => r.cf === "High" && r.phi !== null);
    state.pinned = (firm[0] || sorted(ROWS)[0]).id;
    render();
    if (window.ResizeObserver) {
      let raf = 0;
      new ResizeObserver(() => {
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(() => renderChart(lastVisible));
      }).observe(svg.parentNode);
    } else {
      window.addEventListener("resize", () => renderChart(lastVisible));
    }
  }

  init();
})();
