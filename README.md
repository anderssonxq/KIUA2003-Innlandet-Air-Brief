# Innlandet Air Brief

**KIUA-2003 Compulsory 2: plan and walking skeleton**  
Team: Brage Andersson and Aleksandr Alohins

A Python workflow that turns MET Norway's Hamar air-quality forecast into a
source-linked Norwegian draft bulletin. Five stages acquire data, validate a
complete local day, calculate facts, obtain a bounded local-model selection,
and validate and render the result. Python determines the numbers and wording;
the model selects and orders verified facts.

The proposed users are Hamar information staff and activity organisers preparing
a dated environmental-information update. [Local evidence](docs/impact_sources.md)
supports that scope; user demand, time savings and health benefits remain
unvalidated. The workflow uses public environmental data and keeps output local.

The report and its prompt/meeting appendices are delivered separately through
Overleaf. **The separate compiled PDF must contain the real GitHub repository
URL, and the assessor must be able to access that repository.** This ZIP contains
the runnable project and supporting documentation, with no LaTeX or PDF files.

## Requirements

- Python **3.11 or later** and an x64 CPU; Windows 11 x64 is the team's intended
  platform. A GPU is unnecessary for this small model.
- Internet access for installation and live MET requests.
- Approximately **510 MB of runtime/model downloads**, plus space for extraction
  and the Python environment. No model API account or key is required.

Keep `.gitattributes` committed: it preserves exact bytes for hashed fixtures,
context and evidence files when checking out the project on Windows or Linux.

## Windows setup — PowerShell

Extract or clone the repository, then open PowerShell in the project folder
containing `README.md`, `requirements.txt`, `scripts` and `src`. Run the following
commands from that folder.

Create the virtual environment here; activation and execution-policy changes
are unnecessary.

```powershell
py -3 --version
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_runtime.py
```

The setup helper downloads **llama.cpp b11669** and
**Qwen2.5-0.5B-Instruct Q4_K_M** into `.runtime/`. The publisher downloads are
pinned by SHA-256; a mismatch stops setup. Binaries are excluded from the
repository. `tzdata`, installed from `requirements.txt`, supplies the Europe/Oslo
timezone database on Windows.

## Run the complete workflow

Start with the included real source snapshot, fetched on **27 October 2026**.
This uses historical source data and performs a **new local-model inference**:

```powershell
.\.venv\Scripts\python.exe scripts\run_demo.py --source fixture --date 2026-10-28 --output data\output\demo01
.\.venv\Scripts\python.exe -m src.verify --output data\output\demo01
Get-Content data\output\demo01\bulletin.md -Encoding utf8
```

The launcher starts a local model server when needed, runs all five stages
unattended, verifies the saved output, and stops the server it started. An
already-running local server is left running. Fixture mode uses the explicit
clock `2026-10-27T16:25:25Z` and labels its bulletin as a historical example.

Expected results:

| Check | Expected value |
|---|---|
| Location | Hamar municipality 3403, Innlandet county 34 |
| Coverage | 24 hourly records for 28 October; one interval aggregate excluded |
| Peak AQI | Approximately 1.839 at 17:00 +01:00 |
| Minimum AQI | Approximately 1.635 at 00:00 +01:00 |
| Category | All 24 hourly values are `lite` |
| Acceptance | Pipeline prints `PASS: 14 checks`; saved-output verification prints `PASS` |

Use a **new output directory for each run**, such as `demo02`. Existing run
directories are rejected so old successful output cannot hide a failed run.
Model choices or token counts may vary; numerical facts are checked against the
saved source.

## Tests and offline evidence checks

These commands need Python and `requirements.txt`, but no model or network:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m src.evaluate
.\.venv\Scripts\python.exe -m src.verify --output docs\evidence\live_run
.\.venv\Scripts\python.exe -m src.verify --output docs\evidence\windows_run
```

The starter suite includes valid, boundary and rejection cases. Tests of model
interfaces use explicit test doubles; they are not evidence of real inference.
The two verifier commands recompute the bundled outputs from their saved source
and check the decision and budget without calling a model.

## Live source run

After setup, calculate tomorrow's date in **Europe/Oslo** rather than reusing the
historical fixture date:

```powershell
$forecastDate = .\.venv\Scripts\python.exe -c "from datetime import datetime, timedelta; from zoneinfo import ZoneInfo; print((datetime.now(ZoneInfo('Europe/Oslo')).date() + timedelta(days=1)).isoformat())"
.\.venv\Scripts\python.exe scripts\run_demo.py --source live --date $forecastDate --output data\output\live01
.\.venv\Scripts\python.exe -m src.verify --output data\output\live01
```

Use `live02` or another fresh output directory for the next run. Live mode uses
the real clock and rejects stale sources or incomplete day coverage; it does not
permit a historical `--as-of` override. Responses are cached until `Expires`,
then requested conditionally when `Last-Modified` is available. Cache use is
recorded in the manifest, and the fetcher does not retry automatically.

## Linux equivalent

From the project root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/setup_runtime.py
.venv/bin/python scripts/run_demo.py --source fixture --date 2026-10-28 --output data/output/demo01
.venv/bin/python -m src.verify --output data/output/demo01
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m src.evaluate
.venv/bin/python -m src.verify --output docs/evidence/live_run
.venv/bin/python -m src.verify --output docs/evidence/windows_run
```

## Configuration and limits

The default local model has no model-API charge or API credential. Configuration
comes from process environment variables; `.env.example` documents them. `.env`
is gitignored and **is not automatically loaded**.

```powershell
$env:LOCAL_LLM_URL = "http://127.0.0.1:8080"
$env:MET_USER_AGENT = "KIUA2003-InnlandetAirBrief/0.1"
$env:AIRBRIEF_STOP = "1"  # Reject a new run.
Remove-Item Env:AIRBRIEF_STOP  # Permit a new run again.
```

Only a loopback model URL is accepted. Once the repository exists, add its real
URL to the identifying User-Agent; MET requires application identification and
recommends a reachable contact/site. Keep secrets and runtime files out of Git.

One generation call is allowed, with caps of **3,072 prompt tokens**,
**256 completion tokens** and **4,096 total tokens**. Context files are limited
to 16 KiB, tokenisation is checked before generation, and timeouts bound network
and model calls. Local inference still consumes time, memory and electricity.

The model receives a fact ledger and four context files. It cannot execute
source text, browse, run shell commands or add medical recommendations. Source
JavaScript formulas are never executed. Personal-data compliance relies on the
fixed environmental source; the contact-key/email guard is not a general detector.

## Outputs and recorded runs

Successful runs write source responses and a manifest, normalised records,
`facts.json`, the prompt/context hashes, model response and decision, token
budget, validation record, and `bulletin.json` / `bulletin.md`. These artifacts
make each stage inspectable. Passing checks establishes consistency with the
source; it does not establish forecast accuracy or practical usefulness.

Four saved run bundles are retained under `docs/evidence/`: `live_run/`,
`fixture_run/`, `cold_start_run/` and `windows_run/`. The
[original run record](docs/first_run.md) preserves actual commands, output and the
observed proxy failure/repair. Historical Linux model runs used 1,196 tokens.
The [Windows record](docs/windows_run_20261029.md) describes the supplied fixture
run files received on 29 October, which record 1,195 tokens and passed independent
saved-output recomputation on Linux. That check did not execute a new Windows
model run or fetch live MET data from Windows.

The Windows derivative replaces only the model's user-profile path with its
GGUF basename; 13 other supplied files remain byte-identical. The
[import manifest](docs/windows_evidence/20261029/artifact_import.json) records
original/packaged hashes and that redaction.

## Project documentation

- [SPEC.md](SPEC.md): scope, success/rejection criteria, stages and the planned
  usefulness comparison.
- [Source verification](docs/source_verification.md) and
  [local context](docs/impact_sources.md): MET provenance/terms and the local rationale.
- [Decision record](docs/decision_record.md): chosen scope and rationale.
- [Prompt log](docs/prompt_log.md) and
  [lecturer correspondence](docs/lecturer_feedback.md): supporting provenance for
  the separately delivered report.

The implementation is in `src/`, setup and launchers in `scripts/`, runtime
context in `context/`, and valid/rejected example inputs in `data/fixtures/`.
`AGENTS.md` gives instructions for future coding work.

## Sources and third-party components

- [MET API documentation](https://api.met.no/weatherapi/airqualityforecast/0.1/documentation)
- [MET terms](https://api.met.no/doc/TermsOfService)
- [MET licensing](https://www.met.no/en/free-meteorological-data/Licensing-and-crediting)
- [Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF), Apache 2.0
- [llama.cpp b11669](https://github.com/ggml-org/llama.cpp/releases/tag/b11669), MIT
- [llama.cpp server API](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)

MET data are attributed under CC BY 4.0. Fixtures and bulletins are transformed
extracts, not endorsed official products. Runtime/model binaries are downloaded
from the original publishers and are not redistributed with this project.
