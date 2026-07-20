# Sources & Licensing

This corpus aggregates PDFs from several origins under different terms. There is
**no blanket license covering the fixtures** — see `LICENSE.txt` for how the
Apache-2.0 grant is scoped, and treat licensing as per-file.

Provenance is recorded in two places that must agree: the `source` / `license`
fields in `manifest.json` (authoritative, machine-readable) and the summaries
below (human context and open questions).

## Blocking review items

These must be resolved before the repository is made public.

| # | Item | Files |
|---|------|-------|
| 1 | pdf.js suite licensing — see below | 216 |
| 2 | Root-level real-world documents, provenance unrecorded | 36 |
| 3 | `broken/` fixtures, provenance unrecorded | 16 |
| 4 | `analysis/` fixtures, provenance unrecorded | 16 |

### 1. `corpus/pdfjs/` — Mozilla pdf.js test suite

216 files whose filenames follow pdf.js conventions (`bugNNNNNN.pdf`,
`issueNNNN.pdf`, `prNNNN.pdf`), indicating they came from the
[pdf.js](https://github.com/mozilla/pdf.js) test suite.

**These are not simply "Apache-2.0".** Apache-2.0 covers the pdf.js *source
code*. It does not cover the PDFs in its test suite, which were largely attached
to bug reports by third parties and retain their original owners' rights.
Upstream pdf.js does not redistribute a significant portion of its own test
corpus for exactly this reason: those files exist in the repository as `.link`
stubs pointing at external URLs rather than as committed binaries.

Required before public release:

- Determine which of the 216 are committed upstream and which are `.link`-only.
  Anything in the second group should be treated as not redistributable here
  either, and referenced by URL rather than vendored.
- Record actual terms per file, or narrow the set to files that are clearly
  redistributable.

Until then these carry `"license": "unknown - REVIEW"` in the manifest.

### 2. Root-level `corpus/*.pdf` — assorted real-world documents

Collected real-world PDFs whose provenance predates this manifest. Each needs a
source and license confirmed. Checklist below.

### 3. `broken/` — regression fixtures that fail to parse

Files that historically failed to parse, retained for future investigation.
Never tested, never used as CI inputs. Provenance mostly unknown; several use
pdf.js / poppler naming and are likely from those suites. Lower risk than the
tested corpus, since they are not distributed as working examples — but still
unresolved.

### 4. `analysis/` — large real-world documents

16 large real-world PDFs migrated from the core repository's
`test_analysis/`, kept for investigation and profiling. Never tested, never used
as CI inputs. Filenames are overwhelmingly Brazilian government and institutional
documents; if that holds, most are likely public records, but each still needs
its terms recorded. Checklist below.

## Resolved provenance

### `corpus/pdf-association/pdf20examples/`

7 PDF 2.0 example files from the PDF Association
[pdf20examples](https://github.com/pdf-association/pdf20examples) repository.
Terms still to be transcribed here, but the origin is unambiguous.

### `corpus/custom/`

12 files authored for Vanilla.PDF (encryption / signing / minimal samples).
Internal, distributable with the project.

### `corpus/certificates/`

6 generated test signing certificates (`.pfx`). Internal test fixtures only —
not real credentials, no trust path, safe to commit.

`TestUser3.pfx` previously lived in the core repository at
`scripts/TestUser3.pfx`. It was moved here so that every path in `manifest.json`
resolves inside this checkout; bindings that never clone the core repo need it
to exercise `corpus/certificate_encrypted_s4.pdf` and `_s5.pdf`. The core repo
copy should be removed as part of the migration.

## Personal data review

Fixtures are scanned for personal data before import: document info dictionary,
XMP metadata, filled AcroForm field values, embedded files, and the certificates
inside digital signatures. Anything carrying an identifying record of a living
individual is rejected rather than imported.

**Scope limit:** that pass covers metadata and structure, not rendered page
text. A document can carry personal data in its text while its metadata looks
innocuous, so page text needs its own check; it has so far only been
spot-checked.

What the scan found in the fixtures that were kept:

| File | Finding |
|------|---------|
| 32 fixtures | Carry an apparent personal name in `/Author` or `dc:creator`. Mostly document authors already publicly attributed on published works — a name alone, already attached to a public document, is much weaker exposure. |
| `corpus/pdfjs/issue6006.pdf` | Email address in metadata. |

Stripping `/Author` and `dc:creator` corpus-wide was considered and rejected: it
would alter the files' bytes and therefore change what the parser is being
tested against.

Files checked and cleared, so they are not re-examined every review:

| File | Why it is fine |
|------|----------------|
| `corpus/custom/Granizo-signed.PDF` | Signer is `CN=TestUser3` — the project's own test certificate, not a real identity |
| `corpus/request_for_taxpayer.pdf` | Blank W-9 template; its three filled fields hold placeholder junk |
| `broken/Wilberforce-PUN-05172017.pdf` | A "Know Your Rights" publication; the name is its title, not a data subject |
| `analysis/portaria-gm-md-no-3-572-...pdf` | Signature is an organisational certificate (Imprensa Nacional), no natural person |

## Distribution

Fixtures are published as three separate release assets — `corpus.tar.gz`,
`broken.tar.gz`, `analysis.tar.gz` — rather than one bundle. The core build needs
`corpus/` alone, so a single archive would make every CI run download roughly
three times what it reads. Each asset carries its own SHA256 in `SHA256SUMS`, so
consumers pin only what they use.

`analysis/` is the largest set (99 MB) and the least often needed; keeping it a
separate asset is what stops it from becoming a tax on every build, the way it
was while it lived in the core repository.

## Review checklist — root-level corpus (36 files)

| File | Source | License |
|------|--------|---------|
| `corpus/19005-1_FAQ.PDF` | _TODO_ | _TODO_ |
| `corpus/296333333-pdfSample.pdf` | _TODO_ | _TODO_ |
| `corpus/AdobeXMLFormsSamples.pdf` | _TODO_ | _TODO_ |
| `corpus/Castles_SATURN1000.pdf` | _TODO_ | _TODO_ |
| `corpus/Everyday.pdf` | _TODO_ | _TODO_ |
| `corpus/Granizo.pdf` | _TODO_ | _TODO_ |
| `corpus/MPK_SLOVLEX.pdf` | _TODO_ | _TODO_ |
| `corpus/Park-University-USA.pdf` | _TODO_ | _TODO_ |
| `corpus/Report.pdf` | _TODO_ | _TODO_ |
| `corpus/SP_274-2007.pdf` | _TODO_ | _TODO_ |
| `corpus/access2finance_financial_intermediaries_privacy_statement_en.pdf` | _TODO_ | _TODO_ |
| `corpus/accessible_pdf_webinar_session1.pdf` | _TODO_ | _TODO_ |
| `corpus/acro6_cg_ue.pdf` | _TODO_ | _TODO_ |
| `corpus/bps_park_rpk.pdf` | _TODO_ | _TODO_ |
| `corpus/certificate_encrypted_s4.pdf` | _TODO_ | _TODO_ |
| `corpus/certificate_encrypted_s5.pdf` | _TODO_ | _TODO_ |
| `corpus/example.pdf` | _TODO_ | _TODO_ |
| `corpus/excerpts.pdf` | _TODO_ | _TODO_ |
| `corpus/guide-to-driving-test.pdf` | _TODO_ | _TODO_ |
| `corpus/j130013du1.pdf` | _TODO_ | _TODO_ |
| `corpus/jpdfunit_aShortIntroduction.pdf` | _TODO_ | _TODO_ |
| `corpus/manual-memorias.pdf` | _TODO_ | _TODO_ |
| `corpus/manual.pdf` | _TODO_ | _TODO_ |
| `corpus/parrishfull.pdf` | _TODO_ | _TODO_ |
| `corpus/pdf-example-encryption.original.pdf` | _TODO_ | _TODO_ |
| `corpus/pdf-example-password.original.pdf` | _TODO_ | _TODO_ |
| `corpus/pdf-test.pdf` | _TODO_ | _TODO_ |
| `corpus/pdf.pdf` | _TODO_ | _TODO_ |
| `corpus/pdfSample.pdf` | _TODO_ | _TODO_ |
| `corpus/pdf_open_parameters.pdf` | _TODO_ | _TODO_ |
| `corpus/pdftest2.pdf` | _TODO_ | _TODO_ |
| `corpus/request_for_taxpayer.pdf` | _TODO_ | _TODO_ |
| `corpus/s2010135x20500290.pdf` | _TODO_ | _TODO_ |
| `corpus/sample-encrypted-rc4-40-rev3.pdf` | _TODO_ | _TODO_ |
| `corpus/sample.pdf` | _TODO_ | _TODO_ |
| `corpus/statistika-kriminalita-2019.pdf` | _TODO_ | _TODO_ |

individual consents to redistribution, or drop the file.

## Review checklist — broken fixtures (16 files)

| File | Source | License |
|------|--------|---------|
| `broken/(EN) Samsung UE75NU7172 Manual.pdf` | _TODO_ | _TODO_ |
| `broken/20131231103232738561744.pdf` | _TODO_ | _TODO_ |
| `broken/3F4E2F8DB55F4E11A1CB3D7D70FE9F9B85865A23949594914F4DBB8574D02BDA.pdf` | _TODO_ | _TODO_ |
| `broken/SP800-22b.pdf` | _TODO_ | _TODO_ |
| `broken/Wilberforce-PUN-05172017.pdf` | _TODO_ | _TODO_ |
| `broken/bug1020226.pdf` | _TODO_ | _TODO_ |
| `broken/chinese_names_中文的名字-2.pdf` | _TODO_ | _TODO_ |
| `broken/g070002ep1.pdf` | _TODO_ | _TODO_ |
| `broken/issue2391-1.pdf` | _TODO_ | _TODO_ |
| `broken/issue3371.pdf` | _TODO_ | _TODO_ |
| `broken/issue6010_1.pdf` | _TODO_ | _TODO_ |
| `broken/issue6010_2.pdf` | _TODO_ | _TODO_ |
| `broken/itext_sample.pdf` | _TODO_ | _TODO_ |
| `broken/missing_header.pdf` | _TODO_ | _TODO_ |
| `broken/pr6531_1.pdf` | _TODO_ | _TODO_ |
| `broken/pr6531_2.pdf` | _TODO_ | _TODO_ |

1986 Rumelhart/Hinton/Williams Nature paper — almost certainly not
redistributable. `broken/SP800-22b.pdf` is a NIST publication (US government
work, likely public domain).

## Review checklist — analysis fixtures (16 files)

| File | Source | License |
|------|--------|---------|
| `analysis/1TAConvnion839458.2016Cacoal.RO.pdf` | _TODO_ | _TODO_ |
| `analysis/29_portaria_agu_n__402_-_06092012_.pdf` | _TODO_ | _TODO_ |
| `analysis/4o-termo-aditivo-ao-contrato-operacional-especifico-fca-e-mrs.pdf` | _TODO_ | _TODO_ |
| `analysis/Flora2020digital.pdf` | _TODO_ | _TODO_ |
| `analysis/MapaPipe2019.pdf` | _TODO_ | _TODO_ |
| `analysis/Plano_1208925_assinado_Plano_de_trabalho_Espac807o4_0_IFAL_ArapiracaRioLargo_28_05_2020__002_.pdf` | _TODO_ | _TODO_ |
| `analysis/Portaria20nC2BA835_condecine.pdf` | _TODO_ | _TODO_ |
| `analysis/documento-de-interface-de-software-monitriip-dis-v3-0.pdf` | _TODO_ | _TODO_ |
| `analysis/edital-32.pdf` | _TODO_ | _TODO_ |
| `analysis/gabarito-edital-151-2023.pdf` | _TODO_ | _TODO_ |
| `analysis/plano-nacional-educacao-2014-2024-2ed-1.pdf` | _TODO_ | _TODO_ |
| `analysis/portaria-gm-md-no-3-572-de-29-de-junho-de-2022.pdf` | _TODO_ | _TODO_ |
| `analysis/producao-integrada-no-brasil.pdf` | _TODO_ | _TODO_ |
| `analysis/revista_a_defesa.pdf` | _TODO_ | _TODO_ |
| `analysis/rg_2020_fnde.pdf` | _TODO_ | _TODO_ |
| `analysis/volume1rev2_momento5000_siopproducao_202408292000.pdf` | _TODO_ | _TODO_ |
