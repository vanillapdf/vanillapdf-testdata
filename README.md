# vanillapdf-testdata

Shared PDF test corpus for [Vanilla.PDF](https://github.com/vanillapdf/vanillapdf)
and its language bindings (`vanillapdf.net`, `vanillapdf.py`, …).

This is a **data repository**, not a library. It has no build system. Consumers
pin it to a tag or commit and read `manifest.json` to learn what each file is
and how it is expected to behave.

It exists so that cloning the core repository does not drag ~95 MB of PDF
fixtures along with it.

> **Licensing is per-file, not per-repository.** The Apache-2.0 grant in
> `LICENSE.txt` covers this repository's own content — the manifest, docs and
> scripts — and explicitly does *not* cover the fixtures. See `SOURCES.md`.

## Status

The manifest, licensing and tooling are in place. **The fixture files themselves
have not been imported yet**, so the data directories do not exist in the tree
yet. `manifest.json` already describes all 309 expected files, so it is the
specification the import must satisfy — including which candidates were rejected
by the personal-data review in `SOURCES.md` and must not be imported.

## Layout (target)

```
corpus/          Actively-tested fixtures. Consumed by CI across all bindings.
  custom/        vanillapdf-authored samples (encryption, signing, minimal)
  pdfjs/         Files originating from the Mozilla pdf.js test suite
  pdf-association/pdf20examples/   PDF 2.0 conformance examples
  certificates/  Test signing certificates (.pfx)
broken/          Fixtures that fail to parse. NOT tested — kept for future
                 investigation of parser failures. Do not wire into CI.
analysis/        Large real-world documents kept for investigation and
                 profiling. NOT tested. Do not wire into CI.
manifest.json    Per-file expectations: category, passwords, skip flags, source.
SOURCES.md       Provenance and per-file licensing, plus open review items.
scripts/         Validation tooling.
```

## manifest.json

Every fixture has an entry keyed by its **repo-relative path**:

```json
"corpus/custom/example_128-aes.pdf": {
  "category": "encrypted",
  "user_password": "test",
  "owner_password": "testik",
  "source": "vanillapdf internal",
  "license": "internal"
}
```

| Field | Meaning |
|-------|---------|
| `category` | `valid` \| `encrypted` \| `certificate` \| `broken` \| `analysis` |
| `user_password` / `owner_password` | Passwords for encrypted files |
| `certificate` | Repo-relative path to the PKCS#12 file for certificate-encrypted files |
| `skip` | Capabilities to skip: `process`, `save`, `edit`, `incremental_save` |
| `expect` | For `broken` / `analysis`: expected failure mode (`unknown` until analysed) |
| `tested` | `false` for `broken` and `analysis` files (never executed by CI) |
| `source` / `license` | Provenance — see `SOURCES.md` |

Keys are full paths rather than bare filenames on purpose: basenames collide
across directories (`corpus/manual.pdf` vs `broken/(EN) Samsung UE75NU7172
Manual.pdf` under case-insensitive comparison), and the old basename-keyed
config could not express that.

**Every path in this file — including `config.merge_file` and
`config.signing_certificate` — resolves against the root of this repository.**
Nothing points outside the checkout, so bindings that never clone the core
repository can still resolve every fixture.

The top-level `config` block holds fixtures shared across tests rather than
belonging to any single one.

### `license` vocabulary

| Value | Meaning |
|-------|---------|
| `internal` | Authored by the Vanilla.PDF project; distributable with it |
| `See SOURCES.md` | Folder-level terms recorded in `SOURCES.md` |
| `unknown - REVIEW` | **Unresolved.** Must be cleared before this repo is public |
| `unknown` | Unresolved, on an analysis-only fixture that is never distributed as a test input |

## Consuming this repo

Fixtures are published as **release assets**, not consumed from git. Each data
directory is its own archive, so the core build downloads `corpus.tar.gz` alone
rather than the ~194 MB the full history holds.

**CMake / C++ core** — fetched at configure time, gated on tests:

```cmake
if(VANILLAPDF_ENABLE_TESTS)
  include(FetchContent)
  FetchContent_Declare(vanillapdf_testdata
    URL      https://github.com/vanillapdf/vanillapdf-testdata/releases/download/v1/corpus.tar.gz
    URL_HASH SHA256=<copy from that release's SHA256SUMS>
  )
  FetchContent_MakeAvailable(vanillapdf_testdata)
endif()
```

Pin `URL_HASH`. Without it a re-cut release changes the fixtures underneath a
consumer with no signal; with it, CMake refuses to build instead.

**Watch the extracted layout.** The archive contains a single top-level
`corpus/` directory, and CMake's extraction strips exactly one such level. So
`${vanillapdf_testdata_SOURCE_DIR}` *is* the corpus root — a fixture is at
`${vanillapdf_testdata_SOURCE_DIR}/custom/minimalist.pdf`, not
`.../corpus/custom/minimalist.pdf`. Manifest keys keep their `corpus/` prefix, so
strip it when resolving against `SOURCE_DIR`.

Note that the core repo globs fixtures and generates its certificate header at
**configure** time, so a cold cache makes `cmake` itself network-dependent.
Consumers should offer an override pointing at an existing local checkout
rather than forcing a fetch.

**Bindings** — read `manifest.json`, resolve each key against the checkout root,
and drive the file according to its `category`. Skip anything with
`"tested": false`.

## Validating

```bash
python scripts/validate_manifest.py            # schema + internal consistency
python scripts/validate_manifest.py --strict   # also require every file on disk
```

`--strict` will fail until the fixtures are imported. CI runs the non-strict
form today; flip it once the import lands.

## Releasing

Pushing a `v*` tag builds the archives and publishes them. To produce the same
artifacts locally:

```bash
python scripts/build_release.py           # writes dist/*.tar.gz + SHA256SUMS
python scripts/build_release.py --only corpus
```

Archives are reproducible — identical inputs give a byte-identical file and the
same SHA256, so re-running a release cannot invalidate the hashes consumers have
pinned. That is why the script controls tar member metadata and the gzip
timestamp by hand instead of calling `shutil.make_archive`.

## Versioning

Tagged `vN`. Consumers pin a tag and its asset hash, and bump on purpose, so a
corpus change never silently alters a downstream project's test results.
