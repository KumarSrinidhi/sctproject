# Publishing the dataset on Zenodo (DOI)

Zenodo's GitHub integration installs a webhook, so it needs the repository owner's admin rights. Until the
owner sets it up, upload the dataset bundle by hand instead. It takes about ten minutes.

**Before you publish, settle the repository question.** The repository is public, and its git history still
holds third-party files that may not be redistributed (see "Third-party files in the git history" in
`LICENSE-DATA.md`). The bundle itself is clean. But its `README.txt` and `CITATION.cff`, and the *Related
works* field below, point readers to the repository from a permanent record. Fix the history (or point
`homepage` in `data/dataset.yaml` at a clean repository) before step 5. Reserving the DOI (steps 3–4) is
safe now.

## 1. Build the bundle

```bash
argus build
```

```bash
argus release bundle
```

This writes `dist/ARGUS-dataset-v<version>.zip` (for example `ARGUS-dataset-v1.2.0.zip`). It refuses to
run if the data differ from the released tag of the same version, so a bundle can never carry the wrong
version label. It holds the dataset files only:
- the published CSVs (`thermal_conductivity_dataset.csv`, `paper_inventory.csv`, `extraction_log.csv`,
  `uncertain_measurements.csv`, `unusable_sources.csv`), `datapackage.json` and `CITATION.cff`;
- from `data/`: `dataset.yaml`, `CHANGELOG.md`, `curation_log.yaml`, `exclusions.yaml`, `tombstones.yaml`,
  `processed/measurements_enriched.csv` and the per-paper records in `records/`;
- three generated files: `LICENSE.txt` (what the licence covers inside the archive), `README.txt` and
  `SHA256SUMS.txt`.

It contains no code and no third-party papers. Rebuilding it gives the same bytes on any machine, whatever
the checkout's line endings: CSVs are stored with CRLF and every other text file with LF.
- `SHA256SUMS.txt` is identical everywhere.
- The zip file itself is identical too, given the same zlib build.

Every field you need for the form below is in `.zenodo.json`, generated from `data/dataset.yaml`.

## 2. Optional: a dry run on the sandbox

[sandbox.zenodo.org](https://sandbox.zenodo.org) is a separate test site with its own account; its DOIs
are not real. Do steps 3–5 there first if you want to see the form without consequences.

## 3. Create the upload (zenodo.org)

1. Log in at [zenodo.org](https://zenodo.org) and click **New upload**.
2. **Files:** drag in `dist/ARGUS-dataset-v1.2.0.zip`.
3. **Digital Object Identifier:** answer *No* to "Do you already have a DOI?" and click **Get a DOI now!**.
   This reserves the DOI without publishing.
4. Fill in the form from `.zenodo.json`:

   | Field | Value |
   |---|---|
   | Resource type | Dataset |
   | Title | the `title` in `.zenodo.json` (v1.2.0: ARGUS: Source-verified thermal conductivity of BN- and AlN-filled polymer composites) |
   | Publication date | the `publication_date` (v1.2.0: 2026-10-25) |
   | Creators | Kumar, Aniket; Reddy, Rao Kumar Srinidhi (type: Person; add ORCID iDs and affiliations if you have them) |
   | Description | the `description` in `.zenodo.json`, then the `notes` sentence |
   | Licenses | Creative Commons Attribution 4.0 International |
   | Keywords | the nine `keywords` in `.zenodo.json` |
   | Version | the `version` (1.2.0) |
   | Related works | the `related_identifiers` in `.zenodo.json`: *Is supplemented by*, URL `https://github.com/KumarSrinidhi/sctproject`, resource type Software. Add it only once the repository question above is settled. |
   | Visibility | Public |

5. Click **Save draft**. Do **not** publish yet.

## 4. Send the reserved DOI

Send the reserved DOI (it looks like `10.5281/zenodo.1234567`). It is then added to `data/dataset.yaml`
(`doi:` and `publisher: Zenodo`) and committed to `main`, so that:
- `CITATION.cff`, `.zenodo.json`, the README, `LICENSE-DATA.md` and the course report cite it;
- a rebuilt bundle carries it in `README.txt` and `CITATION.cff`.

The data stay those of tag `data-v1.2`; only the metadata change. Check the rebuilt bundle again before
uploading it: open the zip, read `README.txt`, and confirm the DOI appears there.

## 5. Replace the file and publish

1. In the draft, delete the old zip and upload the rebuilt `dist/ARGUS-dataset-v1.2.0.zip`.
2. Click **Publish**.
3. Record the published file's sha256 (`argus release bundle` prints it) in `data/CHANGELOG.md`.

Publishing is permanent: the files of a published version cannot be changed or deleted. A later dataset
release becomes a **New version** of the same record, with its own DOI plus a DOI that always points to
the latest version.

## Later: switching to the GitHub integration

With a clean history, the repository owner can enable it at **zenodo.org → GitHub**. Every GitHub Release
then becomes a new Zenodo version automatically, using `.zenodo.json` for the metadata.
