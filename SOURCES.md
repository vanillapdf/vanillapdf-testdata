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
| 1 | Root-level real-world documents, provenance unrecorded | 37 |
| 2 | `broken/` fixtures, provenance unrecorded | 8 |
| 3 | `analysis/` fixtures, provenance unrecorded | 12 |
| 4 | `corpus/pdfjs/issue5909.pdf` — no longer present upstream | 1 |

### 1. Root-level `corpus/*.pdf` — assorted real-world documents

Collected real-world PDFs whose provenance predates this manifest. Each needs a
source and license confirmed. Checklist below.

### 2. `broken/` — fixtures the parser cannot yet handle

8 files that fail the open→parse→process→save→edit pipeline. Never tested, never
used as CI inputs. Provenance mostly unknown; several use pdf.js / poppler naming
and are likely from those suites. Lower risk than the tested corpus, since they
are not distributed as working examples — but still unresolved.

### 3. `analysis/` — large real-world documents

12 large real-world PDFs migrated from the core repository's `test_analysis/`.
Never tested, never used as CI inputs. Filenames are overwhelmingly Brazilian
government and institutional documents; if that holds, most are likely public
records, but each still needs its terms recorded. Checklist below.

## Resolved provenance

### `corpus/pdfjs/` — Mozilla pdf.js test suite

216 files copied from [pdf.js](https://github.com/mozilla/pdf.js) (`test/pdfs`).

They are **not** "Apache-2.0" — that covers the pdf.js *source code*, not the
PDFs in its test suite, many of which came from third-party bug reports. But they
are files Mozilla itself redistributes. pdf.js commits test PDFs it judges *not*
redistributable as `.link` stubs pointing at external URLs rather than as
binaries; upstream currently holds 972 committed PDFs against 459 such stubs, and
**none of our 216 are `.link`-only**.

Provenance was verified by comparing git blob SHAs against the upstream tree:
205 byte-identical, 10 drifted since the copy was taken, 1 (`issue5909.pdf`) no
longer present upstream. Each file records its state in `manifest.json`.

The personal-data scan covered all 216 and found only author-name metadata and a
single email address — no identifying records — so they are retained.

When taking further fixtures from upstream, apply the same rule: only files
Mozilla commits as binaries, never `.link` stubs.

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
| `analysis/portaria-gm-md-no-3-572-...pdf` | Signature is an organisational certificate (Imprensa Nacional), no natural person |

## Distribution

Fixtures are published as three separate release assets — `corpus.tar.gz`,
`broken.tar.gz`, `analysis.tar.gz` — plus a standalone `manifest.json` and
`SHA256SUMS`, rather than one bundle. The core build needs
`corpus/` alone, so a single archive would make every CI run download roughly
three times what it reads. Each asset carries its own SHA256 in `SHA256SUMS`, so
consumers pin only what they use.

`manifest.json` ships twice on purpose: inside every archive, where it cannot
desync from the data and keeps manifest keys resolving directly against the
extraction root; and standalone, so bindings and configure-time enumeration can
read the contract without a 50 MB download.

`analysis/` (43 MB) is the least often needed; keeping it a separate asset is
what stops it from becoming a tax on every build, the way it was while it lived
in the core repository.

## Promotion

`broken/` and `analysis/` are staging, not a graveyard. As the parser matures,
fixtures graduate into `corpus/` and start running in CI.

A fixture is promoted when it passes the full open→parse→process→save→edit
pipeline **and** covers something `corpus/` does not already exercise. Passing
alone is not sufficient: the harness runs one ctest per file across every build
configuration, so a document that merely duplicates existing coverage costs
runtime and returns nothing. Such files are dropped rather than promoted.

To promote: move the file, set `category` (`valid`, or `encrypted` if it carries
passwords), remove `expect` and `tested`, and record in `note` what unique
coverage justified it — otherwise the reasoning is lost and the question gets
reopened in a year.

## Review checklist — root-level corpus (37 files)

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
| `corpus/chinese_names_中文的名字-2.pdf` | _TODO_ | _TODO_ |
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

## Review checklist — broken fixtures (8 files)

| File | Source | License |
|------|--------|---------|
| `broken/SP800-22b.pdf` | _TODO_ | _TODO_ |
| `broken/bug1020226.pdf` | _TODO_ | _TODO_ |
| `broken/g070002ep1.pdf` | _TODO_ | _TODO_ |
| `broken/issue2391-1.pdf` | _TODO_ | _TODO_ |
| `broken/itext_sample.pdf` | _TODO_ | _TODO_ |
| `broken/missing_header.pdf` | _TODO_ | _TODO_ |
| `broken/pr6531_1.pdf` | _TODO_ | _TODO_ |
| `broken/pr6531_2.pdf` | _TODO_ | _TODO_ |

1986 Rumelhart/Hinton/Williams Nature paper — almost certainly not
redistributable. `broken/SP800-22b.pdf` is a NIST publication (US government
work, likely public domain).

## Review checklist — analysis fixtures (12 files)

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
| `analysis/portaria-gm-md-no-3-572-de-29-de-junho-de-2022.pdf` | _TODO_ | _TODO_ |
| `analysis/rg_2020_fnde.pdf` | _TODO_ | _TODO_ |
