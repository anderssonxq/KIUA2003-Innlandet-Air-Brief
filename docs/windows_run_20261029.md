# Windows fixture reproduction and artifact review — 29 October 2026

## Evidence and scope

The user supplied PowerShell commands, terminal output and the bulletin, followed
by `windows01_evidence.zip` containing 14 original run files. The assistant opened
all 14 files, checked their consistency and ran the saved-output verifier on the
uploaded results in the Linux development environment. The original files and the
repository derivative both passed. This did not execute a new model call or run
the program on the user's Windows computer.

The exact original execution timestamp, Windows edition/build and installed
runtime/model binary hashes are not established by these files. Source retrieval
and `as_of` times are historical fixture clocks, not execution timestamps. The
date in this heading records receipt and review of the evidence.

This Windows reproduction evidence is distinct from the directly captured
27 October Linux runs in first_run.md. A documented repository copy is included
in [evidence/windows_run/](evidence/windows_run/). The console text is preserved in
[windows_evidence/20261029/console.txt](windows_evidence/20261029/console.txt).
The local profile/download path in each PowerShell prompt is replaced with
`<project-root>`; commands, reported results and bulletin text are retained.

## Reported commands

```powershell
.\.venv\Scripts\python.exe scripts\run_demo.py --source fixture --date 2026-10-28 --output data\output\windows01
.\.venv\Scripts\python.exe -m src.verify --output data\output\windows01
Get-Content data\output\windows01\bulletin.md -Encoding utf8
```

## Reported results

| Item | User-supplied result |
|---|---|
| Source mode | Historical fixture for 28 October 2026 |
| Local model | Started on loopback; one schema-constrained inference reported |
| Coverage | 24 hourly records; one interval record excluded |
| Token usage | 1,172 prompt + 23 completion = **1,195 / 4,096** |
| Pipeline validation | `PASS: 14 checks` |
| Verification inside the demo | Saved output recomputed against saved source; `PASS` |
| Separate verifier command | Saved output recomputed against saved source; `PASS` |
| Peak displayed AQI | 1.839 at 17:00 +01:00, category `lite` |
| Minimum displayed AQI | 1.635 at 00:00 +01:00, category `lite` |
| Forecast reference time | 2026-10-27T06:00:00+00:00 |

The bulletin labels the output as a historical example, distinguishes a forecast
from measurements and includes MET attribution, source and licence links.
The displayed facts agree with the expected saved-fixture results in the README.

The uploaded budget and model-response records confirm **1,195** total tokens;
the response contains 23 completion token IDs and parses to the saved decision.
The Windows token count is **not** the Linux token count: the historical Linux
run recorded 1,172 + 24 = 1,196. Both reported totals are below the 4,096 cap.
The completion-token difference does not change the reported deterministic
facts or pass results; its precise cause has not been investigated.

## Independent artifact verification

The verifier recomputed normalization, facts and the rendered JSON/Markdown from
the saved source, checked source hashes and validated the saved decision and
budget. Both the original extracted output and the repository copy returned:

```text
PASS: saved output recomputed against saved source; no model call made
```

The command for the included repository copy is:

```powershell
.\.venv\Scripts\python.exe -m src.verify --output docs\evidence\windows_run
```

Additional file checks established that the raw data match the project's real
historical fixtures; all four context hashes match; the saved schema equals the
current schema; the prompt reconstructs from current context and saved facts;
and the model response parses to `decision.json`. Prompt/completion counts agree
between the response and budget, token arithmetic is correct and the saved
validation record contains 14 distinct checks. The retained
[artifact review](windows_evidence/20261029/artifact_review/) contains
`consistency_checks.json` and the original/packaged verifier stdout records,
`verify_original_stdout.txt` and `verify_packaged_stdout.txt`. Repeated revision
and document-build logs remain outside this implementation repository.

### Documented metadata redaction

The original `agent_response.json` contained a local Windows user-profile path
in its `/model` field. The repository copy replaces only that JSON value with
the existing filename `qwen2.5-0.5b-instruct-q4_k_m.gguf`. Model response content,
token IDs/counts and timings are unchanged. The other 13 files are byte-identical
to the upload, including their Windows line endings. Original and packaged hashes
and the exact redaction pointer are recorded in
[artifact_import.json](windows_evidence/20261029/artifact_import.json).

The original uploaded archive and extracted files were preserved unchanged
outside the repository. The raw archive is not embedded in this GitHub copy
because it would reproduce the identifying local profile path.

## Scope and limits

The transcript and checked run files support the reported Windows fixture
reproduction with local inference, deterministic checks, rendering and
saved-output verification. Artifact consistency does not authenticate the original
host or re-run the model/tokenizer. Fixture mode does not demonstrate a new MET data fetch on Windows.
It is not a Windows unit-test run, a run of the full stress-test plan, a meeting
report or evidence that both students have reviewed the complete submission.

The files were imported from the user's archive rather than reconstructed from
the pasted transcript. Historical Linux evidence and its measurements remain
unchanged. No additional Windows run or OS-version check is introduced as a C2
submission requirement by this review.

## Setup clarification

The initial installation attempt was made from the outer extraction directory,
where `requirements.txt` was absent. The user reported:

```text
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

The assistant directed the user into the inner `innlandet-air-brief` directory
before creating the virtual environment and running installation. The README
now makes that extraction step explicit. The subsequent success transcript is
the user-supplied result above. No application-code repair was needed for this
working-directory issue.
