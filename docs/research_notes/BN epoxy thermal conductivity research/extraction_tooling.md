# Tooling for a literature-mined materials-property dataset (discovery → OA full text → extraction → digitization → validation/provenance)

Scope: rebuilding an ad-hoc pipeline (260 thermal-conductivity rows of epoxy + BN/AlN composites from 95 papers) as a tested, reusable package. Only open-access / licensed routes, no paywall circumvention. Research done 2026-10-22. Items marked **(CHANGED 2025–26)** are recent changes that break older code or assumptions.

---

## 1. Discovery & metadata APIs (OpenAlex, Crossref, Semantic Scholar, Europe PMC, Unpaywall, CORE, arXiv, ChemRxiv): endpoints, limits, auth, licence/abstract availability

### Takeaway
The big 2025–26 change is **OpenAlex**. It moved to API keys with a daily USD budget: keys were required from Feb 2026, and calls are billed by type (singleton lookups free, list/filter $0.10 per 1k, search $1 per 1k, PDF/TEI download $10 per 1k). It also rewrote its backend ("Walden", Nov 2025). Separately, **Crossref** tightened public and polite-pool limits from 1 Dec 2025, with list queries at 1 rps public and 3 rps polite. Europe PMC (JATS + licence field per record) and Unpaywall (`best_oa_location`) remain the most reliable keyless OA routes. Semantic Scholar works without a key but shares one unauthenticated pool across all users, and a new key starts at only 1 rps.

### Cited Findings

**OpenAlex (CHANGED 2025–26)**
- Rate limits (docs "last updated October 15, 2026"): 10 req/s without a key, 30 req/s with a free key or prepaid usage, 50 req/s on an annual plan. Semantic search is limited to 1 req/s. Searches with more than 5 boolean operators get 1/5/25 req/s (no key/free/annual). — [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)
- Key mechanics: pass `api_key=YOUR_KEY` as a query parameter or as an `Authorization: Bearer` header. A free key "raises your daily budget 10×" and is **required for cursor paging past the first page**. Keys can also be created programmatically via `POST https://api.openalex.org/api-keys` with an `email` field, but they only work after the owner clicks an emailed activation link. Until then calls return 403 `key_not_activated`. — [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)
- Daily budget: a free key gets $1/day (`daily_budget_usd_after_activation: 1.0`). The budget is visible in the response headers `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Credits-Used` and `X-RateLimit-Reset` (seconds until midnight UTC). `GET https://api.openalex.org/rate-limit?api_key=...` returns usage. A per-second 429 costs nothing. — [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication); [OpenAlex authentication reference](https://help.openalex.org/api-reference/authentication)
- Hard query limits: `per_page` ≤ 100; `sample` ≤ 10,000; basic paging stops at 10,000 results, so use cursor paging (which needs a key) beyond that; ≤ 100 OR-values per filter. — [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)
- Pricing (blog post "New Features and Usage-Based Pricing", 24 Feb 2026): "API keys are now required". Each key gets $1 of free usage per day. Per-call costs: singleton work lookup by DOI/ID free; list+filter $0.0001 ($0.10 per 1,000); search $0.001 ($1 per 1,000); PDF/XML download $0.01 ($10 per 1,000). — [OpenAlex blog (author page listing the 24 Feb 2026 post)](https://blog.openalex.org/author/jason)
- The 16 Jan 2026 roadmap had previewed a *credit* model instead (singleton 1 credit, list 10, PDF 100, vector search 1,000). The Feb 2026 launch used USD costs, so older third-party docs quoting credits are stale. — [OpenAlex blog](https://blog.openalex.org/author/jason); [CASRAI news (secondary)](https://casrai.org/news/openalex-api-keys-mandatory-usage-based-pricing-2026)
- Timeline per the OpenAlex changelog, as summarised in search results (I could not fetch the changelog page itself): keys "recommended" 4 Feb 2026 and "required" 13 Feb 2026. — [OpenAlex changelog](https://help.openalex.org/hc/en-us/articles/38868153578263-Changelog). **Conflict:** the current (Oct 2026) docs say "basic queries" still work with no key on a small budget, and sources disagree on whether the keyless budget is $0.10/day or $0.01/day. — [OpenAlex authentication reference](https://help.openalex.org/api-reference/authentication); [OpenAlex example costs](https://help.openalex.org/access/example-costs/)
- Practical free-tier arithmetic: $1/day covers unlimited singleton lookups, 10,000 list calls, 1,000 searches, or 100 PDF downloads. — [OpenAlex docs via search summary](https://help.openalex.org/access/example-costs/)
- **Walden rewrite (CHANGED):** beta from 1 Oct 2025 (opt in with `data-version=2`). It went live on 3 Nov 2025, "powering all of OpenAlex", with 190M new works added. Legacy data stayed reachable via `data-version=1` for "a few weeks" only. — [OpenAlex blog](https://blog.openalex.org/author/jason)
- **OA full-text content API (new):** OpenAlex hosts PDFs and GROBID TEI XML for its ~60M OA works. The pattern is `https://content.openalex.org/works/{work_id}.pdf?api_key=...`, or `.grobid-xml` for TEI. Each download costs $0.01 and needs a key; a free key allows about 100 files/day. Filter for available content with `has_content.pdf:true`, combinable with `best_oa_location.license`. For bulk downloads with retry/resume there is the `openalex-official` CLI. Page counts differ: ~60M PDFs, ~43M TEI files, or "50M+". — [OpenAlex get-content docs](https://docs.openalex.org/how-to-use-the-api/get-content); [OpenAlex full-text PDFs](https://developers.openalex.org/download/full-text-pdfs); [OpenAlex blog](https://blog.openalex.org/author/jason)
- The mailto/polite-pool mechanism is **not mentioned** on the current OpenAlex rate-limit or authentication pages. — [OpenAlex rate limits & authentication](https://help.openalex.org/how-to-use-the-api/rate-limits-and-authentication)

**Crossref REST API (CHANGED 1 Dec 2025)**
- Announced 5 Nov 2025, effective 1 Dec 2025 (the first revision since 2013):
  - Public pool: single record 5 req/s (concurrency 1); list queries/filters 1 req/s (concurrency 1).
  - Polite pool: single DOI 10 req/s (concurrency 3); list 3 req/s (concurrency 3).
  - Polite access still means a valid email in the `mailto` parameter.
  - Metadata Plus, the XML API and OAI-PMH are unchanged, and Metadata Plus is recommended for production stability.
  — [Crossref blog: Announcing changes to REST API rate limits](https://crossref.org/blog/announcing-changes-to-rest-api-rate-limits/)
- A later Crossref community post keeps those figures, adds an `x-rate-limit-type` response header, and says to back off on HTTP 429 (via search summary). — [Crossref community: Refining REST API limits](https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137)
- TDM/licence route: publishers that enable mining register a stable licence URL (`<license_ref>`) and full-text links. The documented researcher workflow is: get the DOI metadata, check the licence and full-text fields, compare the licence against your whitelist, then follow the link. "The absence of a license does not mean that the full text can be used without one." Access control stays with the publisher. — [Crossref TDM for researchers](https://crossref.org/documentation/retrieve-metadata/rest-api/text-and-data-mining-for-researchers); [Crossref TDM services (support)](https://support.crossref.org/hc/en-us/articles/215750183-Crossref-Text-and-Data-Mining-Services)

**Semantic Scholar Academic Graph API**
- Unauthenticated requests are limited to "1000 requests per second shared among all unauthenticated users" and may be throttled under load. The introductory rate for an API key is "1 RPS on all endpoints". Some endpoints require a key; you request one via a form and it arrives by email. The corpus is stated as 214M papers and 2.49B citations. Bulk datasets: S2AG (JSON) and S2ORC (full-text NLP corpus). There is a separate API License Agreement. — [Semantic Scholar API product page](https://www.semanticscholar.org/product/api)
- Fields (third-party schemas; I did not reach the official docs): `abstract` is nullable, and some publishers and older papers lack it. `openAccessPdf` is an object `{url, status, license}` or null. — [ToolUniverse S2 client source](https://zitniklab.hms.harvard.edu/ToolUniverse/_modules/tooluniverse/semantic_scholar_tool.html); [Apify S2 scraper docs](https://apify.com/crawlerbros/semanticscholar-scraper)

**Europe PMC REST**
- Verified live: `https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<doi>&format=json&resultType=core` returns per-record `isOpenAccess`, `inEPMC`, `inPMC`, `hasPDF`, `hasSuppl`, `license` (e.g. "cc by"), `abstractText`, `fullTextUrlList` (each link carries an availability label such as "Open access" or "Subscription required") and `pmcid`. — [Europe PMC REST search (live response)](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1038/s41467-024-45563-x&format=json&resultType=core)
- Verified live: `https://www.ebi.ac.uk/europepmc/webservices/rest/{PMCID}/fullTextXML` returns JATS (`<article>`, JATS Archiving DTD 1.4). The XML includes `<permissions>`/`<license>` (CC BY 4.0), `<sec>`, `<table-wrap>` and `<fig>` elements, which makes it machine-checkable licence and table structure. — [Europe PMC fullTextXML (PMC10869356)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10869356/fullTextXML)
- No key or registration is needed, and query syntax supports field operators like `TITLE:x AND OPEN_ACCESS:y`. — [Apify Europe PMC actor (secondary)](https://apify.com/crawlerbros/europe-pmc-scraper); [rOpenSci europepmc](https://docs.ropensci.org/europepmc/). Full text is available only for the PMC Open Access subset, so check the OA flag first. — [DeepMind science-skills Europe PMC guide (secondary)](https://skillselion.com/skills/google-deepmind/science-skills/literature-search-europepmc). Max page size is 100 (client code comment). — [Scientific-Papers-MCP Europe PMC driver](https://glama.ai/mcp/servers/@benedict2310/Scientific-Papers-MCP/blob/646da8d8af653f6b833f3725bae4cafc38a9428e/src/drivers/europepmc-driver.ts)
- Note: `europepmc.org/RestfulWebService` and `europepmc.org/developers` returned HTTP 403 to my automated fetcher, while the `ebi.ac.uk` API host worked. — (observed this session)

**Unpaywall**
- Requests must include `email=` at the end of the URL. The asked-for limit is ≤ 100,000 calls/day; heavier users should take the database snapshot. — [Unpaywall REST API](https://unpaywall.org/products/api)
- Unpaywall now runs on the OpenAlex infrastructure. The migration made the API about 10× faster (500 ms → 50 ms) and changed data for ~23% of works (~10% of `oa_status`, ~5% of `is_oa`). The schema is unchanged, but **`oa_locations.evidence` and `oa_locations.updated` are deprecated** (post undated in results). — [OpenAlex blog: Major update to Unpaywall database](https://blog.openalex.org/major-update-to-unpaywall-database)
- `best_oa_location` is chosen by an algorithm that prefers publisher-hosted copies, and `is_best` flags it inside `oa_locations`. — [roadoi docs](https://docs.ropensci.org/roadoi/articles/intro.html)

**CORE, arXiv, ChemRxiv**
- CORE API v3: an API key is required; results cap at 10,000 per query set, 100 per page; bulk access is through the CORE Dataset dumps (registration required) (secondary source). Records expose `fullText` and `downloadUrl` fields. — [SMU library API guide](https://researchguides.smu.edu.sg/api-list/scholarly-metadata-api); [Scientific-Papers-MCP CORE driver](https://glama.ai/mcp/servers/@benedict2310/Scientific-Papers-MCP/blob/646da8d8af653f6b833f3725bae4cafc38a9428e/src/drivers/core-driver.ts)
- arXiv: one request every 3 seconds, single connection, applying across all machines you control. Metadata is CC0. Full text remains under copyright (mostly the arXiv non-exclusive licence) and may be retrieved and used for research but not re-served. Bulk options are S3 and OAI-PMH. — [arXiv API Terms of Use](https://info.arxiv.org/help/api/tou.html)
- ChemRxiv: "Open API compatible". Community code calls `https://chemrxiv.org/engage/chemrxiv/public-api/v1/items` with `term`, `sort`, `limit` and reads `itemHits[].item`. The footer shows "Public API 1.0.2741". I did not reach the official API docs. — [ChemRxiv FAQ](https://chemrxiv.org/engage/assets/public/chemrxiv/term/faq.htm); [decode-elm utils.py (HF)](https://huggingface.co/spaces/mehradans92/decode-elm/blob/ae7891a8ca1abeb40a57b951c064b2575c73bdf3/utils.py)

### Inferences
- **Recommended discovery stack:**
  1. OpenAlex (free key, stored in an env var) for recall-oriented search plus `best_oa_location.license` and `abstract_inverted_index`.
  2. Crossref (polite `mailto`) for authoritative metadata and TDM licence/link fields.
  3. Europe PMC for the JATS full text and licence of PMC-deposited papers.
  4. Unpaywall to resolve a legal OA copy for each DOI.
  5. Semantic Scholar only as a supplementary recall source.
- **Budget implications:** the current 95-paper dataset is tiny relative to the OpenAlex budget. Singleton DOI lookups are free, so resolve candidates by DOI after a few dozen search/list calls. But OpenAlex PDF/TEI downloads (~100/day free) become the binding constraint at scale, so prefer Europe PMC JATS when available.
- **Client changes:** the per-second limits require a shared rate limiter per host (a token bucket), honouring `Retry-After` and backing off on 429. Crossref list concurrency is 1 (public) or 3 (polite), so don't fan out Crossref list queries.
- **Licence gating:** record the licence string (OpenAlex/Unpaywall/Europe PMC/Crossref) as a gating field before any full-text retrieval. Only fetch when the licence or OA status is compatible, and store "no licence" as "do not mine". This matches Crossref's guidance that no licence ≠ permission.
- **Walden pinning:** OpenAlex IDs and counts changed with Walden (190M works added). Any cached OpenAlex query results from before Nov 2025 should be re-run, and the pipeline should record the API "data version" or date in provenance.

### Gaps
- Europe PMC's official server-side rate limit could not be confirmed (its docs pages returned 403 to my fetcher). Use client-side throttling, e.g. ≤ 10 req/s as in community clients.
- CORE v3's current rate limits (tokens per minute or day by tier) are unverified: the official docs at api.core.ac.uk and core.ac.uk returned 403.
- I found no official statement on whether OpenAlex still honours `mailto` for any purpose now that keys exist. I also could not resolve the conflicting keyless daily budget figures ($0.10 vs $0.01).
- The official Semantic Scholar Graph API reference (field-level licence and abstract rules, current key tiers above 1 rps) was not fetched.
- The share of Crossref records with deposited abstracts was not checked. Abstract availability from Crossref depends on publisher deposit.

---

## 2. Full-text parsing: JATS XML and PDF-to-structure tools (GROBID, Nougat, Marker, PyMuPDF, Docling, pdfplumber/Camelot) and their table quality

### Takeaway
For OA papers with JATS (Europe PMC) or TEI (OpenAlex `.grobid-xml`), parse the XML directly. `<table-wrap>` gives structured tables with no layout inference. For PDFs, the best independent benchmark (OmniDocBench) ranks pipeline tools first on tables: MinerU (TEDS 78.6), then Mathpix (77.0). General VLMs come close (Qwen2-VL-72B 76.8, GPT-4o 72.0), Marker sits mid-pack (67.6) and Nougat is poor (39.9). GROBID is best for header and reference metadata but not for tables. Docling (MIT) and Marker (Apache-2.0 code, restricted weights) are the practical open choices, but table-heavy pages still need human checks.

### Cited Findings
- **OmniDocBench (arXiv 2412.07626v2, 25 Mar 2025).** End-to-end English results:

  | Tool | Table TEDS ↑ | Text edit distance ↓ |
  |---|---|---|
  | MinerU | 78.6 | 0.061 |
  | Mathpix | 77.0 | 0.105 |
  | Qwen2-VL-72B | 76.8 | 0.096 |
  | GPT-4o | 72.0 | 0.144 |
  | Marker | 67.6 | 0.08 |
  | InternVL2-76B | 63.0 | 0.353 |
  | GOT-OCR | 53.2 | 0.189 |
  | Nougat | 39.9 | 0.365 |

  The authors conclude that pipeline tools such as MinerU and Mathpix perform best across sub-tasks. Docling and PyMuPDF were not in this table. — [OmniDocBench](https://arxiv.org/html/2412.07626)
- **2023 multi-tool benchmark (10 tools, academic PDFs):** GROBID was best for metadata and reference extraction, followed by CERMINE and Science Parse. For tables, Adobe Extract was best, but table performance "is much lower than for other content elements". — [Meuschke et al., A Benchmark of PDF Information Extraction Tools](https://arxiv.org/abs/2303.09957v1)
- **GROBID:** Apache-2.0 licence. Extracts header, references, and full-text structure (paragraphs, sections, figures, tables, data-availability statements) with PDF coordinates. Output is TEI XML. Runs via Docker, REST service, batch, or Java API. Self-reported reference extraction is ~0.87 F1 on 1,943 PMC PDFs and ~0.90 on 2,000 bioRxiv PDFs; there are no table-specific accuracy figures. — [GROBID docs](https://grobid.readthedocs.io/en/latest/Introduction/)
- **Docling (IBM, now docling-project):** MIT code licence; the models carry their own licences. Inputs include PDF, DOCX, PPTX, XLSX, HTML, images and LaTeX. Outputs are Markdown, HTML, DocTags and lossless JSON (the `DoclingDocument` model). It has a VLM pipeline (`docling --pipeline vlm --vlm-model granite_docling`, granite-docling-258M). Install with `pip install docling`; Python ≥ 3.10 (3.9 dropped in v2.70.0). No table accuracy claims on the README. — [Docling GitHub](https://github.com/docling-project/docling)
- **Marker (datalab):** the README now states an **Apache-2.0** code licence. Model weights use a modified AI Pubs Open Rail-M licence: free for research, personal use and startups under $5M funding/revenue; other commercial use is paid. `TableConverter` outputs HTML tables, rebuilding digital tables from the text layer and falling back to a VLM. `--use_llm` improves difficult tables (multi-page, spans). Self-reported olmOCR-bench scores: Marker 76.0 overall vs Docling 50.3; Marker table score 73.4 (balanced). — [Marker GitHub](https://github.com/datalab-to/marker). (Older Marker releases were GPL-3.0 per my prior knowledge, not re-verified; check the licence of the exact version you pin.)
- **Community and anecdotal table comparisons (weak evidence):**
  - PDF-Bench reports pdfplumber at 93.4% table-structure accuracy on table-heavy docs and a 2.6% Docling failure rate (methodology unverified). — [pdf-parser-benchmark](https://github.com/applied-artificial-intelligence/pdf-parser-benchmark)
  - A single-paper test found Docling found all 3 tables but lost column alignment in multi-row headers; MinerU preserved merged cells better. — [CodeSOTA Docling vs MinerU](https://www.codesota.com/ocr/docling-vs-mineru)
  - Another community benchmark notes merged headers are a weak area for Docling. — [BestHub parser benchmark](https://www.besthub.dev/articles/open-source-pdf-parser-benchmark-mineru-granite-docling-paddleocr-vl-and-xberg-9f184b033c66)
- **ChatExtract on XML tables:** tables whose XML-to-text conversion was broken were counted as errors "because humans could not extract them either". This shows the source format, not the LLM, is often the limiting factor. — [Polak & Morgan 2024 (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10882009)
- **OpenAlex TEI is GROBID output:** OpenAlex serves `.grobid-xml` TEI for ~43M OA works. A TEI parser therefore covers both self-run GROBID and OpenAlex-cached content. — [OpenAlex get-content docs](https://docs.openalex.org/how-to-use-the-api/get-content)

### Inferences
- **Source-format priority ladder:**
  1. Publisher/PMC JATS XML (Europe PMC `fullTextXML`): exact tables and licence.
  2. OpenAlex GROBID TEI.
  3. OA PDF parsed with Docling (MIT, easiest licence for a course project), using Marker or MinerU as a second opinion on table pages.
  4. A VLM on rendered table images only as a fallback, with human verification.

  Record `parser_name` + `parser_version` per extracted table in provenance.
- **Tables:** implement a `TableExtractor` interface with a JATS adapter (lxml over `<table-wrap>/<table>`, keeping `<label>`, `<caption>`, `<table-wrap-foot>` because units and footnotes often live there), a TEI adapter, and a PDF adapter. Store the raw extracted table (CSV/HTML) as an immutable artifact keyed by DOI + table label so value rows can point at it.
- **Cross-checking parsers:** for a 95→few-hundred-paper corpus, running two PDF parsers and flagging disagreeing cells for review is cheap and catches the merged-header failures reported for Docling.

### Gaps
- No independent 2025–26 benchmark tested Docling, Marker, GROBID, MinerU and pdfplumber/Camelot together on *scientific tables*. Docling was absent from OmniDocBench's main table.
- JATS-specific Python libraries (e.g. `pubmed_parser`, other JATS parsers) were not researched this session, so their maintenance status and licences are unverified.
- PyMuPDF's licence (AGPL/commercial dual licence per prior knowledge) and Nougat's weight licence (non-commercial per prior knowledge) were **not re-verified**.
- Camelot's current status was not checked.

---

## 3. Materials text-mining: ChemDataExtractor 2, MatSciBERT/MatBERT, and LLM-based property extraction (reported precision/recall; human-in-the-loop patterns)

### Takeaway
Purpose-built LLM workflows report ~90% precision/recall on simple material–value–unit triplets: ChatExtract with GPT-4 reached 90.8% P / 87.7% R. Table extraction reaches ~91% P / 89% R (ChatExtract tables), with MaTableGPT at F1 up to 96.8%. Rule-based ChemDataExtractor 2 is far lower in head-to-head tests (57% P / 31% R on bulk modulus). Its auto-generated thermoelectric database (which includes thermal conductivity) had 82.25% precision. Every strong result relies on (a) a cheap relevance filter before the LLM, (b) redundant verification prompts, and (c) human-curated gold sets for scoring. Thermal conductivity was one of 24 properties in the largest polymer LLM extraction to date.

### Cited Findings
- **ChatExtract** (Polak & Morgan, *Nat Commun* 15:1569, 2024; CC BY 4.0). Bulk-modulus test set of 100 sentences / 179 triplets, overall P/R:

  | Model | Precision | Recall |
  |---|---|---|
  | GPT-4 (gpt-4-0314) | 90.8% | 87.7% |
  | GPT-3.5 | 70.1% | 65.4% |
  | LLaMA2-chat 70B | 61.5% | 62.9% |

  Other results from the paper:
  - **Ablation:** GPT-4 without the follow-up verification questions drops to 42.7% P / 98.9% R. The doubt-inducing follow-ups are what buy precision.
  - **Tables (GPT-4):** table classification 95% P / 98% R; datapoint extraction 91% P / 89% R.
  - **Figures:** relevance classification 80% P / 82% R. Figure data was flagged for human extraction, not extracted.
  - **ChemDataExtractor2 baseline:** 57% P / 31% R on bulk modulus; 49.2% P / 35.1% R on critical cooling rates.
  - **Critical-cooling-rate database:** 76.9% P / 63.1% R raw, 91.9% / 84.2% after standardisation. The abstract says 91.6/83.6 (internal inconsistency).
  - **Workflow:** sentence relevance filter (~1 in 100 sentences relevant) → passage = title + previous sentence + target → single- vs multi-valued branch → strict Yes/No follow-up checks → discard on any "No". Standardisation still needed manual work, regex and pymatgen.
  - **Code and data:** figshare 10.6084/m9.figshare.22213747.

  — [Polak & Morgan 2024 (PMC10882009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC10882009)
- **Dagdelen et al.** (*Nat Commun* 15:1418, 2024; CC BY): fine-tuned GPT-3 and Llama-2 for joint NER + relation extraction, with JSON or English-sentence outputs. Exact-match F1 for host–dopant: Llama-2 0.821, GPT-3 0.726, against baselines seq2rel 0.496 and MatBERT-Proximity 0.390. General-materials and MOF relations are much lower under exact match (≈0.29–0.62). Manual scoring of General-JSON (GPT-3) gives formula 0.943, applications 0.832, structure/phase 0.829, description 0.704. Training needed 400–650 annotated examples per task. Human-in-the-loop: intermediate models pre-annotate and a human corrects. At n = 300 examples, annotation time per abstract fell 57% compared with n = 1; models trained on < 50 examples often emitted invalid JSON. — [Dagdelen et al. 2024, Europe PMC JATS (PMC10869356)](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10869356/fullTextXML)
- **Polymer literature LLM extraction** (Gupta, Mahmood, Shetty, Adeboye, Ramprasad, *Communications Materials* 5:269, 2024):
  - Scale: ~2.4M full-text articles → 681k polymer articles → >1M records of 24 properties for >106k polymers.
  - **Thermal conductivity is one of the 24 properties**: 5,574 values from GPT-3.5 (full text), 10,300 from MaterialsBERT (full text), 1,429 from MaterialsBERT (abstracts).
  - Two-stage filter before any LLM call: a property-specific heuristic (string and dictionary match on curated synonyms) passed ~11% of paragraphs. Then a MaterialsBERT NER filter keeps only paragraphs containing a material, property name *and* property value (~3%). The authors say this filter prevents placeholder or hallucinated values.
  - F1 vs a manual gold set (1,000 docs): Tg GPT-3.5 0.67, LlaMa-2 0.64, MaterialsBERT 0.63; bandgap GPT-3.5 0.87/0.85, LlaMa-2 0.77, MaterialsBERT 0.66.
  - Settings and cost: temperature 0.001, no conversation history. The evaluation cost $4.48 per shot strategy (~2.9M tokens); the full run of 716k paragraphs took about a month and ~US$1,200.
  - Data is public via Polymer Scholar.

  — [Gupta et al. 2024 (PDF, Ramprasad group)](https://ramprasad.mse.gatech.edu/wp-content/uploads/2025/01/s43246-024-00708-9.pdf)
- **LLM table extraction for polymer composites** ("How well do LLMs understand tables in materials science?"): the best setup was a multimodal model given the table *image*. It scored 0.910 accuracy for composition extraction and 0.863 F1 for property names. — [NSF PAR record](https://par.nsf.gov/biblio/10539623-how-well-do-large-language-models-understand-tables-materials-science)
- **MaTableGPT** (*Advanced Science*, 2025): GPT-based table extractor using table splitting and follow-up questions to filter hallucinations. Total F1 up to 96.8% on water-splitting catalysis literature. — [MaTableGPT (PMC12021050)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12021050/)
- **Recent (arXiv 2604.07584, 2026):** a priority-based Gemini 3 Pro workflow for spall strength, evaluated on 30 articles / 11,967 data points. Most papers scored above 90% accuracy; the lower scores came from figure-based extraction, not tables. — [From Papers to Property Tables](https://arxiv.org/pdf/2604.07584)
- **ChemDataExtractor 2:** MIT licence; Python 3.9–3.11. Readers for HTML/XML/PDF, chemistry-aware NER, rule-based property grammars, and a table parser. — [CDE2 GitHub](https://github.com/CambridgeMolecularEngineering/chemdataextractor2)
- **CDE-built thermoelectric DB** (Sierepeklis & Cole, *Sci Data* 2022): 22,805 records for 10,641 unique compound names covering five thermoelectric properties including thermal conductivity κ, each linked to temperature. Mined from 60,843 papers (Elsevier, RSC, Springer); precision 82.25%. — [Sierepeklis & Cole 2022 (PMC9587980)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9587980); [figshare dataset](https://figshare.com/articles/dataset/A_Thermoelectric_Materials_Database_Auto-Generated_from_the_Scientific_Literature_using_ChemDataExtractor/19658787)
- **Domain BERTs:**
  - MatSciBERT (npj Comput Mater 2022) reports beating SciBERT on abstract classification, NER and relation extraction. — [MatSciBERT arXiv](https://arxiv.org/pdf/2109.15290)
  - MatBERT improves 1–12% over BERT/SciBERT on three materials NER sets, with larger gains in the small-data limit. — [Trewartha et al. 2022 (PMC9024010)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9024010/)
  - **Contradicting evidence:** MatSci-NLP found MatBERT generally best but SciBERT often beating MatSciBERT. — [MatSci-NLP](https://huggingface.co/papers/2305.08264.md)

### Inferences
- **For epoxy/BN/AlN κ extraction:**
  - Use a deterministic pre-filter: regex for `W/(m·K)`, `W m−1 K−1`, "thermal conductivity", plus filler names, as in Gupta's heuristic filter.
  - Then use an LLM extractor that must return JSON validated by a schema (pydantic). Each value carries a verbatim `source_quote`, which must be verified to occur in the source text (string-match check). This is the same "must be present in the text" rule Gupta used for scoring.
  - Add ChatExtract-style follow-up verification ("Is the filler loading given in wt% or vol%?", "Is this the composite or the neat matrix value?").
- **Expected error profile:** the published numbers (≈0.65–0.9 F1 depending on property complexity) imply a human-verification queue is mandatory for a course dataset. Composite records are multi-valued (filler type, loading + unit basis, κ, measurement method, temperature), which is the regime where ChatExtract recall dropped (multi-valued GPT-4 recall 82.7%). A practical pattern is LLM pre-fill → human accept/correct, as in Dagdelen's pre-annotation, with time savings expected.
- **Gold set:** the existing 260 hand-verified rows are a ready-made gold set. Score any new extractor against them (precision, recall, per-field exact match) in CI before scaling coverage.
- **CDE2 suitability:** CDE2 needs a custom property model for κ of composites (loading, filler), and its baseline recall was low in ChatExtract's tests. It is better used as a cheap pre-filter or NER feature than as the main extractor. This is an inference, not a tested result for κ.

### Gaps
- I found no published extraction benchmark specific to **thermal conductivity of polymer composites** (filler loading + κ + method). Gupta reports per-property counts for κ but F1 only for Tg and bandgap.
- Dagdelen's code repository URL and licence were not verified. The Polymer Scholar data licence was not checked.
- MatSciBERT's NER numbers from the npj article were not retrieved.

---

## 4. Figure digitization: WebPlotDigitizer v5, PlotDigitizer, ChartOCR, LLM/vision chart extraction, and recording digitization uncertainty

### Takeaway
WebPlotDigitizer is now at v5.2. Its frontend is AGPL-3.0, but the "AI Assist" and cloud components are closed source, and an older repository describes v5 as "closed source" (conflicting statements). Manual and semi-automatic digitizers show high inter-coder reliability, but error depends on the graph, not the tool. LLM/VLM digitization now reports ~90% point precision/recall with ~5% positional error on simple two-axis plots (PlotExtract, 2025). Reading values directly from an image with a VLM performs much worse than reconstructing the curve first (54.3% vs 4.2% median relative error in MatDeplot, 2026). A reproducible, script-based digitizer (like the project's colour-mask + tick calibration) with explicit uncertainty fields remains the defensible core.

### Cited Findings
- **WebPlotDigitizer licence and status:**
  - Current docs cite version 5.2. It is described as "a web based utility" combining computer vision and manual inputs. — [Automeris docs](https://automeris.io/docs/)
  - "WPD frontend is distributed under GNU AGPL v3 license"; "Automeris 'AI Assist' and other related cloud based systems are closed source and owned by Automeris LLC." — [automeris-io/WebPlotDigitizer](https://github.com/automeris-io/WebPlotDigitizer)
  - **Conflict:** the archived legacy repository states that v4 and earlier work was paused "in favor of v5 (closed source)", is AGPL v3, and accepts no contributions. — [netopt/WebPlotDigitizer](https://github.com/netopt/WebPlotDigitizer)
- **Reliability evidence for software digitizers:**
  - Drevon et al. (*Behavior Modification* 2017): two coders, 3,596 points from 168 series in 36 graphs; high inter-coder reliability and validity for WPD. — [Drevon et al. 2017](https://journals.sagepub.com/doi/10.1177/0145445516673998)
  - Moeyaert et al. 2016: reliability and validity were independent of the software but dependent on the individual graph. — [summary](https://behavioristbookclub.com/aba-research/assessment-research/reliability--validity--and-usability-of-data-extraction-programs-for-s/)
  - PlotDigitizer was validated on 6,846 points ("nearly perfect" intra- and inter-coder correlations). — [Aydin & Yassikaya 2022](https://avesis.ankara.edu.tr/yayin/6850a7fb-53c9-40be-8454-36085c22774f/validity-and-reliability-analysis-of-the-plotdigitizer-software-program-for-data-extraction-from-single-case-graphs)
  - Cochrane training material: software extraction was faster with slightly higher inter-rater agreement (53.5% vs 51%), and the Cochrane Handbook gives no guidance on figure extraction. — [Cochrane webinar slides (Puljak 2016)](https://training.cochrane.org/sites/training.cochrane.org/files/public/uploads/resources/downloadable_resources/2016_11_webinar_Puljak-extracting-data-from-figures.pdf)
- **PlotExtract** (Polak & Morgan, arXiv 2503.12326, Mar 2025): zero-shot chain-of-thought prompts to multimodal LLMs, with no fine-tuning, for two-axis plots. On plots judged extractable it gets >90% precision, ~90% recall, and x/y errors "around 5% or lower". The workflow has the LLM regenerate the plot in Python from the extracted data so it can be compared visually against the original. — [PlotExtract arXiv](https://arxiv.org/abs/2503.12326); [search summary of method](https://arxiv.org/html/2503.12326v1)
- **MatDeplot (ICML 2026):** LLMs given MatDeplot-reconstructed curves reach 4.2% median relative error, against 54.3% for VLMs reading chart images directly. — [MatDeplot (ICML 2026)](https://icml.cc/virtual/2026/73589)
- **Fine-tuned VLM for chemistry figures:** Qwen2.5-VL-7B-Instruct was the best base model; LoRA fine-tuning raised point detection by 24% on literature datasets. — [Research Square rs-10090500](https://www.researchsquare.com/article/rs-10090500)
- **Other benchmarks:**
  - A ChemRxiv (Oct 2025) benchmark covers materials figure types: stress–strain curves, heatmaps, contour plots. Its accuracy figures were not retrieved. — [ChemRxiv benchmark](https://www.cambridge.org/engage/chemrxiv/article-details/68f8560daec32c65685fd48b)
  - A blog reports 99–100% accuracy for open-weight models but on synthetic charts (upper bound only). — [Menon Lab blog](https://themenonlab.blog/blog/chart-extraction-validation)
- **ChatExtract figures:** GPT-4 classified figure relevance at 80% P / 82% R. The authors left the actual digitization to humans. — [Polak & Morgan 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10882009)

### Inferences
- **Uncertainty fields per digitized point** (best practice synthesised from the above; no single standard was found):
  - `digitizer_tool` + `version`
  - axis calibration points (pixel ↔ data for ≥ 2 ticks per axis, plus log/linear flag)
  - image resolution (DPI or pixel size of the source figure)
  - `pixel_uncertainty`, converted to data units, e.g. ±0.5–1 px × (data units per px)
  - marker size or line width in px
  - repeat-digitization SD: digitize twice, or by two people or tools, and record the difference, following the inter-coder reliability approach of Drevon/Moeyaert
  - a `value_source = figure` flag with confidence downgraded relative to text/table values
- **Treat LLM chart reading as a second opinion:** run the scripted colour-mask digitizer and a VLM (PlotExtract-style, with plot regeneration for visual diff). Auto-accept only when the two agree within the pixel uncertainty; otherwise queue for review. MatDeplot's result argues against trusting raw VLM numbers.
- **Prefer text or table values:** when a paper reports the same value in text or a table, prefer it over figure-derived values and keep both for cross-validation of the digitizer.
- **Licensing:** WPD v5 desktop/cloud features may be closed. To keep the pipeline open and reproducible, use the AGPL frontend or v4 only manually, and keep the custom scripted digitizer for automation. Calling a closed cloud API adds a non-reproducible dependency.

### Gaps
- ChartOCR and the PlotDigitizer (plotdigitizer.com) licence or pricing were not researched this session.
- WPD v5's automatic extraction algorithms (averaging window, X-step, colour detection) were not documented on the pages fetched, and v5 licence terms for the desktop build are unconfirmed.
- I found no materials-science-specific standard for reporting digitization uncertainty.

---

## 5. Data model & validation tooling: pydantic / pandera / Frictionless (datapackage.json, Table Schema), JSON Schema; versioning (DVC, Git LFS); FAIR; PROV-style provenance; units with pint

### Takeaway
Use pydantic models for row-level records and LLM-output validation, pandera for whole-table checks (MIT; supports pandas, polars and PySpark), and pint for units. pint's offset-temperature rules make °C vs K errors raise exceptions instead of passing silently. Publish as a Frictionless Data Package, but note that Data Package **v2.0** (June 2024) was not yet readable by the Python/R frictionless libraries as of January 2026, so emit v1-compatible descriptors or validate carefully. The known pipeline defects need explicit design: an append-after-reject bug, no idempotency key, non-atomic writes, and an unused normalizer. The fixes are a validation gate that quarantines rejected rows, a deterministic record ID, atomic temp-file + rename writes, and normalization built into the schema.

### Cited Findings
- **Frictionless Data Package v2.0** was released 26 Jun 2024. It comprises four core specs: Data Package, Data Resource, Table Dialect and Table Schema. It aims for no breaking changes and adds a versioning mechanism, categorical data support and easier extension. — [Frictionless blog: Data Package v2 release](https://frictionlessdata.io/blog/2024/06/26/datapackage-v2-release/)
- **(CHANGED/CAVEAT)** A January 2026 community call reported that the R and Python packages "could only handle version 1", so reading a v2 dataset produces errors. — [Frictionless Jan 2026 community call](https://frictionlessdata.io/blog/2026/01/23/monthly-community-call/)
- **pandera:** MIT licence. Supports pandas, polars and PySpark. Two APIs: object-based `DataFrameSchema` + `Column`, and class-based `DataFrameModel` + `Field`. Built-in checks (`Check.ge`, `isin`, etc.) and custom checks. Since v0.24.0 `pandera.pandas` is "the (highly) recommended" import path; top-level imports will be deprecated in 0.29.0. — [pandera GitHub](https://github.com/unionai-oss/pandera)
- **pint offset units:** degC and degF are offset units, with delta counterparts (`delta_degC`) for differences. Adding offset quantities, or adding an absolute to an offset quantity, raises an error. Multiplying or dividing offset quantities raises `OffsetUnitCalculusError` unless `autoconvert_offset_to_baseunit=True`, which converts to kelvin. In multiplicative contexts like `degC/meter` the parser uses the delta unit. — [pint docs: temperature conversion](https://pint.readthedocs.io/en/stable/user/nonmult.html)
- **FAIR:** the FAIR Guiding Principles (Findable, Accessible, Interoperable, Reusable) for scientific data management, Wilkinson et al., *Scientific Data* 2016. — [Wilkinson et al. 2016](https://www.nature.com/articles/sdata201618) (canonical source; not re-fetched this session)
- **W3C PROV:** the W3C PROV family (2013) models provenance as Entities, Activities and Agents with relations such as `wasDerivedFrom`, `wasGeneratedBy` and `wasAttributedTo`. — [W3C PROV Overview](https://www.w3.org/TR/prov-overview/) (canonical; not re-fetched)
- **Versioning tools:** DVC (data version control on top of Git) and Git LFS (large-file pointers in Git) are the standard options. — [DVC docs](https://dvc.org/doc); [Git LFS](https://git-lfs.com) (canonical; not re-fetched)
- **Precedent for provenance and source-presence checks:** Gupta et al. score an extracted record correct only when material, property, value *and* unit are all present in the source paragraph. This verbatim-presence test can be automated. — [Gupta et al. 2024](https://ramprasad.mse.gatech.edu/wp-content/uploads/2025/01/s43246-024-00708-9.pdf)

### Inferences
- **Record model** (pydantic). Each row carries:
  - Measurement fields: `matrix` and `filler` (enums, e.g. BN subtypes h-BN/c-BN/BNNS, AlN), `filler_loading_value`, `filler_loading_basis` (wt% | vol%, required, plus a conversion flag if derived), `surface_treatment`, `kappa_value`, `kappa_unit_raw`, `kappa_W_per_mK` (normalised via pint), `measurement_method` (laser flash, hot disk/TPS, guarded hot plate, …), `measurement_direction` (through-plane/in-plane), `temperature_K`.
  - Provenance fields (below).
- **PROV-lite fields per row:**
  - Entity: `doi`, `openalex_id`, `pmcid`, `source_artifact_sha256` (the exact XML or PDF used), `source_license`, `source_url`, `retrieved_at`.
  - Location: `source_location` (section, table label or figure label) and `source_quote` (verbatim, must be found in the artifact text).
  - Activity: `extraction_method` (rule | llm | manual | digitized), `extractor_version`, `llm_model_id`, `prompt_sha256`, `parser_name`/`parser_version`.
  - Agent: `curator`, `review_status` (pending/accepted/rejected/corrected), `reviewed_at`.
  - Confidence and uncertainty: `confidence`, `digitization_uncertainty` (absolute, in W/m·K).
- **Idempotency key:** `record_id = sha256(doi | source_location | normalized material descriptor | loading+basis | kappa_W_per_mK rounded | temperature)`. Use upserts keyed on `record_id`. A dedup test in CI should fail on duplicate keys.
- **Validation gate:** validators return `(accepted, rejected)` partitions. Only `accepted` reaches the dataset writer; `rejected` goes to `quarantine.jsonl` with the reasons attached. A unit test should assert that rejected rows never appear in the output, which directly targets the logged-but-appended bug.
- **Atomic writes:** write to `file.tmp` in the same directory, `fsync`, then `os.replace(tmp, final)`, which is atomic on POSIX and Windows for same-volume replace. The final CSV/Parquet is regenerated from a canonical JSONL or SQLite store, never edited in place.
- **Unit normalizer:** make normalization a pydantic validator (`model_validator`) so a row cannot exist without a normalised `kappa_W_per_mK`. Use pint with a whitelist of accepted κ units, and store the raw unit string alongside the normalised value.
- **Publication:** a v1-compatible `datapackage.json` with Table Schema field types and constraints mirroring the pydantic model (or generate JSON Schema from pydantic with `model_json_schema()`). Use DVC or Git LFS for raw artifacts (PDF/XML), but only commit artifacts whose licence permits redistribution. Otherwise store DOI + hash only, which matches the arXiv/Crossref licence rules above.

### Gaps
- pydantic v2 specifics, JSON Schema draft versions, `pint-pandas`, and DVC/Git LFS current features were not fetched this session. The claims above about them are generic, and the canonical URLs are cited without re-verification.
- I found no materials-community standard provenance schema for literature-mined property data. The PROV-lite field list is my synthesis.

---

## 6. Existing open pipelines and resources for literature-derived materials datasets (PPPDB, MPDS, Matscholar, Polymer Scholar, ASReview, etc.): what can be reused

### Takeaway
The most reusable pieces found are:
- the ChatExtract code and prompts (figshare);
- Polymer Scholar, which already contains thousands of auto-extracted thermal-conductivity values for polymers and is useful for cross-checking or seeding discovery;
- ChemDataExtractor 2 (MIT) and its thermoelectric κ database;
- ASReview LAB 2.0 for active-learning title/abstract screening, which can replace ad-hoc relevance filtering at the discovery stage.

PPPDB, MPDS and Matscholar were not verified this session.

### Cited Findings
- **Polymer Scholar** (polymerscholar.org) publicly hosts >1M LLM/NER-extracted polymer property records (24 properties), including 5,574 GPT-3.5 and 10,300 MaterialsBERT full-text thermal-conductivity values. — [Gupta et al. 2024](https://ramprasad.mse.gatech.edu/wp-content/uploads/2025/01/s43246-024-00708-9.pdf)
- **ChatExtract** example Python code, extracted databases and assessment data are on figshare (DOI 10.6084/m9.figshare.22213747). The code has "limited error handling". — [Polak & Morgan 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10882009)
- **ChemDataExtractor 2** is MIT-licensed, with table parser and property grammars. Its thermoelectric DB (κ included, 82.25% precision) is on figshare. — [CDE2 GitHub](https://github.com/CambridgeMolecularEngineering/chemdataextractor2); [thermoelectric DB](https://pmc.ncbi.nlm.nih.gov/articles/PMC9587980)
- **ASReview LAB 2.0** (*Patterns*, July 2025):
  - Multiple reviewers can share one AI model, and a project can switch between fast classifiers and transformer models.
  - Models improved with a 24.1% loss reduction vs v1 on the SYNERGY benchmark. The lightweight ELAS u4 model sits in core, and heavier models come via the "Dory" package.
  - Modes: Oracle (screening), Simulation and Exploration.
  - The original method appeared in *Nature Machine Intelligence* (2021).

  — [ASReview LAB 2.0 (PMC12416088)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12416088); [ASReview docs](https://asreview.readthedocs.io/en/latest/about.html); [van de Schoot et al. 2021](https://www.doi.org/10.1038/S42256-020-00287-7)
- **Domain-specific prior data for epoxy/h-BN:**
  - An arXiv percolation paper tabulates epoxy + h-BN-flake κ vs volume fraction, digitized from a prior figure (e.g. matrix κ 0.24 W/m·K, percolation threshold 12.5 vol%). It is a cross-check target for the project's own digitizer. — [arXiv 2209.07635](https://arxiv.org/pdf/2209.07635)
  - A 2021 *Energy and AI* paper trains a semi-supervised NN on BN-sheet/polymer κ using matrix κ, BN diameter, aspect ratio and volume fraction as inputs. This suggests which descriptors to capture. — [Energy and AI 2021 (DOAJ)](https://doaj.org/article/f632833cd15e476388171f88636fc540)

### Inferences
- **Discovery:** export OpenAlex/Crossref/Europe PMC results to RIS/CSV, screen titles and abstracts in ASReview (simulate first using the existing 95 included papers as known relevant), and record the stopping rule in a PRISMA-style log. This replaces ad-hoc keyword filtering with an auditable, reproducible screen.
- **Extraction:** adapt ChatExtract's prompt sequence (relevance → extraction → doubt-inducing verification) to a composite-specific schema. Use Polymer Scholar's κ records as a recall check, i.e. papers it covers that the new pipeline missed. Re-verify every reused value against the original source before inclusion, since its extraction F1 is ~0.65–0.87.
- **Packaging:** structure the pipeline package as `discover/` (API clients with shared rate limiter and cache), `retrieve/` (licence-gated OA fetchers: Europe PMC JATS, OpenAlex TEI/PDF, Unpaywall URL), `parse/` (JATS/TEI/PDF adapters), `extract/` (rule, LLM and manual adapters emitting the same pydantic record), `digitize/`, `validate/` (pydantic + pandera + pint; quarantine), `store/` (atomic, idempotent upsert), and `publish/` (datapackage.json). Each stage should be testable with recorded fixtures (e.g. VCR-style HTTP cassettes) so CI never hits live APIs.

### Gaps
- **PPPDB** (Polymer Property Predictor and Database, U. Chicago), **MPDS** (Materials Platform for Data Science) and **Matscholar** were not researched this session: current availability, API, licence and reusability are unverified. MPDS is commercial per prior knowledge, which is not verified.
- "polyMATe" could not be identified, and no search was run for it.
- No search result described ASReview's native OpenAlex import. Whether it ingests OpenAlex directly (vs RIS/CSV export) is unconfirmed.
- I found no public, curated benchmark dataset of epoxy/BN/AlN κ from the literature comparable to the project's own 260-row set.
