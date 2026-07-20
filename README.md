# vanillapdf-testdata

Shared PDF test corpus for [Vanilla.PDF](https://github.com/vanillapdf/vanillapdf)
and its language bindings (`vanillapdf.net`, `vanillapdf.py`, …).

This is a **data repository**, not a library. It has no build system. Consumers
pin it to a tag or commit and read `manifest.json` to learn what each file is
and how it is expected to behave.

It exists so that cloning the core repository does not drag ~190 MB of PDF
fixtures along with it.

> **Licensing is per-file, not per-repository.** The Apache-2.0 grant in
> `LICENSE.txt` covers this repository's own content — the manifest, docs and
> scripts — and explicitly does *not* cover the fixtures. See `SOURCES.md`.

## Layout

294 fixtures, 110 MB.

```
corpus/    (274)  Actively-tested fixtures. Consumed by CI across all bindings.
  custom/         vanillapdf-authored samples (encryption, signing, minimal)
  pdfjs/          Files originating from the Mozilla pdf.js test suite
  pdf-association/pdf20examples/   PDF 2.0 conformance examples
  certificates/   TestUser3.pfx — decrypts two fixtures; not a test itself
broken/      (8)  Fixtures the parser cannot yet handle. NOT tested.
                  Staging — see Promotion in SOURCES.md.
analysis/   (12)  Large real-world documents for investigation and profiling.
                  NOT tested. Also staging.
manifest.json     Per-file contract: type, status, passwords, skip flags, source.
SOURCES.md        Provenance, licensing, personal-data review, promotion rule.
scripts/          Validation and release tooling.
```

`broken/` and `analysis/` are not a dumping ground — they are the queue. As the
parser matures, fixtures graduate into `corpus/` and start running. `SOURCES.md`
records what a file must prove to earn promotion.

## manifest.json

Every fixture has an entry keyed by its **repo-relative path**:

```json
"corpus/custom/example_128-aes.pdf": {
  "type": "pdf",
  "status": "valid",
  "user_password": "test",
  "owner_password": "testik",
  "source": "vanillapdf internal",
  "license": "internal"
}
```

| Field | Meaning |
|-------|---------|
| `type` | What the artifact is: `pdf` \| `certificate` |
| `status` | Whether the library handles it: `valid` \| `broken` |
| `user_password` / `owner_password` | Passwords for encrypted files |
| `certificate` | Repo-relative path to the PKCS#12 file for certificate-encrypted files |
| `skip` | Capabilities to skip: `process`, `save`, `edit`, `incremental_save` |
| `expect` | For `status: broken`: expected failure mode (`unknown` until analysed) |
| `sha256` | Digest of the fixture; `--strict` verifies it |
| `note` | Why the fixture exists, when that is not obvious |
| `source` / `license` | Provenance — see `SOURCES.md` |

`type` and `status` are deliberately orthogonal, and neither encodes encryption:
a password-protected PDF is `valid` and simply carries `user_password` /
`owner_password`. Making "encrypted" a category would force a false choice, since
such a file is both.

**Enumerate tests as `type == "pdf" and status == "valid"`.** Certificates fall
out by type, staging by status — no directory assumptions, no special cases.

Keys are full paths rather than bare filenames on purpose. The directory records
why a fixture is kept, so the same basename can legitimately exist in both
`corpus/` and `broken/`, which a basename-keyed config cannot express. Paths also
make promotion a visible change rather than a silent one: a file graduating from
`broken/` to `corpus/` changes its key.

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
| `unknown` | Provenance unrecorded — see the review checklists in `SOURCES.md` |

## Consuming this repo

Fixtures are published as **release assets**, not consumed from git. Each data
directory is its own archive, so the core build downloads `corpus.tar.gz` alone
rather than the whole 110 MB repository.

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

Every archive ships `manifest.json` beside its data directory, so after
extraction manifest keys resolve **directly** against the root:

```
${vanillapdf_testdata_SOURCE_DIR}/manifest.json
${vanillapdf_testdata_SOURCE_DIR}/corpus/custom/minimalist.pdf
```

That layout is deliberate. CMake strips a lone top-level directory during
extraction, which would leave keys needing their `corpus/` prefix removed; a
second top-level entry suppresses the strip. Extract several archives into one
root and the same holds — `corpus/…`, `broken/…` and `analysis/…` all resolve,
and the bundled manifest can never disagree with the bytes it arrived with.

Enumerate tests from the manifest rather than globbing: it is the authoritative
list and carries the expectations, and a glob needs a reconfigure to notice a
new fixture.

Note that the core repo globs fixtures and generates its certificate header at
**configure** time, so a cold cache makes `cmake` itself network-dependent.
Consumers should offer an override pointing at an existing local checkout
rather than forcing a fetch.

**Bindings** — read `manifest.json`, resolve each key against the checkout root,
and drive each fixture according to its fields.

## Validating

```bash
python scripts/validate_manifest.py            # schema + internal consistency
python scripts/validate_manifest.py --strict   # also require every file on disk
```

CI runs `--strict` on every push, so a manifest that disagrees with what is
committed fails the build.

## Releasing

Pushing a `v*` tag builds the archives and publishes them. To produce the same
artifacts locally:

```bash
python scripts/build_release.py           # writes dist/*.tar.gz + SHA256SUMS
python scripts/build_release.py --only corpus
```

Archives pin everything that would otherwise vary between checkouts — member
mtime, uid/gid, mode, ordering, and the gzip header timestamp — so rebuilding on
the same machine reproduces the same bytes. That is why the script does this by
hand rather than calling `shutil.make_archive`, which stamps the current time
into both layers.

**Reproducibility does not extend across platforms.** The DEFLATE stream depends
on the zlib build: a zlib-ng runtime and stock zlib produce different bytes for
identical input, so a local rebuild will not match the published `.tar.gz` hash.
The *uncompressed* tar is identical — verified — so this is a compression-layer
artifact, not a content difference.

Content integrity therefore does not rest on archive hashes. Every fixture
carries its own `sha256` in the manifest, which is stable everywhere and is what
`--strict` verifies. Archive hashes serve `URL_HASH`, i.e. download integrity.

## Versioning

Tagged `vN`. Consumers pin a tag and its asset hash, and bump on purpose, so a
corpus change never silently alters a downstream project's test results.
