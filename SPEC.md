# Innlandet Air Brief: Compulsory 2 specification

## Problem and intended users

The proposed task for Hamar information staff and activity organisers is to
prepare a dated Norwegian update from the official municipal air-quality
forecast. The output is a reviewable draft bulletin with structured evidence.
The benefit hypothesis is less transcription and easier checking of place,
forecast issue time, coverage and source. User demand, time savings and practical
benefit have not been demonstrated.

The [official background](docs/impact_sources.md) places this pilot in Hamar's
occasional winter particulate-air-quality context and its dust-control cooperation
with the county and road authorities. The county's public-health profile reports
comparatively favourable particulate conditions. Station observations provide
context; they do not validate the municipal forecast or establish demand for
this tool.

The output is not an official warning, measurement, individual exposure estimate,
medical recommendation, dust-control instruction or automatic publication.
The [decision continuation](docs/decision_record.md#continuation-recorded-29-october-2026)
records retaining Air Brief for C2. The report and its appendices are delivered
separately through Overleaf.

## Scope

- One fixed public geography: Hamar municipality 3403, Innlandet county 34.
- One requested Europe/Oslo calendar date, with complete hourly coverage.
- MET Norway's openly licensed AQI forecast and category descriptor; source
  details and reuse conditions are in [source_verification.md](docs/source_verification.md).
- No personal records, accounts, contact lists, user location or medical data.
- One local Qwen2.5-0.5B-Instruct inference through llama.cpp.
- A model decision about presentation; Python calculates the numerical facts
  and renders the Norwegian sentences.

## Definition of success

A successful run exits zero and produces a local draft whose selected facts can
be recomputed from the saved source. Geographic identity, source freshness,
complete local-day coverage, unique timestamps, units, finite AQI values,
category boundaries, permitted fact IDs, output structure and token limits
must pass deterministic checks. A separate verification command recomputes the
saved output without network access or model inference.

The model selects three distinct fact IDs, including `coverage` and `peak`,
plus either `minimum` or `distribution`, and an allowed opening style. All
output numbers, timestamps, category labels and source references come from
code. Ties select the earliest timestamp. Categories use full-precision values;
displayed AQI is rounded to three decimals.

Readability, the usefulness of the ordering, user demand and the source
forecast's accuracy require judgment or external evidence. Passing software
checks does not establish those properties or guarantee identical model output.

### Planned usefulness evaluation

Use identical saved inputs to compare manual preparation from the official
source, fixed-template rendering and the bounded model-assisted draft. Record
preparation time, factual corrections, missing provenance and clarity judgments
for the same dated-information task. These are proposed measures, not measured
results or additional mechanical acceptance checks. A lack of useful improvement
would support simplifying or reconsidering the approach before the white paper.

## Stages and acceptance

1. Fetch/cache or explicitly load a historical fixture; save source provenance.
2. Normalise; distinguish instantaneous hourly values from interval averages.
3. Compute extrema, coverage and category counts with source-row references.
4. Read bounded context, tokenise and make one schema-constrained local model call.
5. Validate the decision and render a Norwegian JSON/Markdown draft.

The model context consists of `context/task.md`, `context/glossary.md`,
`context/decision.schema.json` and `context/example.json`. These supply its task,
source terminology, allowed response structure and an example. Intermediate
files record the actual prompt, loaded context hashes and model response.

After the documented setup, the complete fixture path is:

```text
python scripts/run_demo.py --source fixture --date 2026-10-28 --output data/output/demo01
```

This performs a new local-model inference using a historical source and its
explicit reference clock. Live mode uses the actual clock and performs or validly
caches an external fetch. An incomplete requested day is rejected. Every run
requires a fresh output directory; see [README.md](README.md) for exact Windows
and Linux commands and expected output.

## Recorded execution evidence

Four saved bundles are retained in `docs/evidence/`: `live_run/`, `fixture_run/`,
`cold_start_run/` and `windows_run/`. [first_run.md](docs/first_run.md) records the
27 October Linux runs, their command output, starter tests and observed failure
and repair. Those model runs used 1,172 prompt plus 24 completion tokens (1,196).

The [Windows run record](docs/windows_run_20261029.md) documents the supplied
fixture transcript and 14 run files received on 29 October. They record
24 hourly values, one excluded interval, 14 passing checks and 1,172 + 23 =
1,195 tokens. Their saved-source output passed independent recomputation on
Linux without a new model call. This does not establish a new Windows model run
or Windows live MET fetch; the exact Windows build and original execution time
remain unestablished.

The Windows repository derivative replaces only the `/model` metadata value in
`agent_response.json` with the actual GGUF basename, removing a user-profile
path. The other 13 files are byte-identical. The
[import manifest](docs/windows_evidence/20261029/artifact_import.json) records
original/packaged hashes and the redaction. `.gitattributes` preserves exact bytes
for hashed fixture, context and evidence files across checkouts.

## Rejection and human control

Missing or duplicate hours, nonlocal data, changed descriptor boundaries,
invalid numbers/units, stale or future reference times, malformed model decisions,
budget violations and unavailable dependencies cause rejection. Failed model
calls are not silently replaced by fixed output.

`AIRBRIEF_STOP=1` stops a new run. Network and inference calls have timeouts.
One generation call is allowed, with caps of 3,072 prompt tokens, 256 completion
tokens and 4,096 total tokens; context files are capped at 16 KiB. No source or
model text is executed as code. Configuration uses process environment variables;
`.env` is ignored by Git and is not automatically loaded.

Only local drafts are written. Human review is required before sharing; the
workflow contains no sending or publication function. Before the demonstration,
the plan is to review the intended audience's need, broaden evaluation, and
investigate input perturbation and dependency failure. Those planned activities
are distinct from the recorded C2 execution evidence.
