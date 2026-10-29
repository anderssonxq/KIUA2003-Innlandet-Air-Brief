# First executed runs and observed evidence

This is the historical record of commands executed on Linux x64 on 27 October 2026. All printed command/result blocks below are preserved unchanged from the original full C2 package, including their original output paths; they do not describe a new run of this GitHub copy. The later user-supplied Windows reproduction and its artifact review are recorded separately in [windows_run_20261029.md](windows_run_20261029.md). These execution records are not student meeting reports.

## Live end-to-end run

The forecast and descriptor each returned HTTP 200 via the network (not cached fallback). The forecast was fetched at 2026-10-27T16:35:11.417888+00:00. The model stage used the real local Qwen2.5-0.5B-Instruct Q4_K_M model through llama.cpp b11669. The wrapper then recomputed the saved output against the saved source. Exit code: **0**.

```text
python scripts/run_demo.py --source live --date 2026-10-28 --output data/output/live_verified
Reusing a healthy local model server.
[1/5] Acquire source=live
[2/5] Normalize and check geographic/time coverage
      24 hourly records; 1 interval record(s) excluded
[3/5] Calculate source-linked facts
[4/5] Run one schema-constrained local model inference
      tokens: prompt=1172 completion=24 total=1196/4096
[5/5] Validate decision and render local draft
PASS: 14 checks; draft saved to data/output/live_verified/bulletin.md
PASS: saved output recomputed against saved source; no model call made
```

## Saved-source run with fresh real inference

This is a historical fixture replay for source data only, with a new real model call. The source clock is explicitly 2026-10-27T16:25:25Z. It is not presented as a current forecast. Exit code: **0**.

```text
python scripts/run_demo.py --source fixture --date 2026-10-28 --output data/output/fixture_verified
Reusing a healthy local model server.
[1/5] Acquire source=fixture
[2/5] Normalize and check geographic/time coverage
      24 hourly records; 1 interval record(s) excluded
[3/5] Calculate source-linked facts
[4/5] Run one schema-constrained local model inference
      tokens: prompt=1172 completion=24 total=1196/4096
[5/5] Validate decision and render local draft
PASS: 14 checks; draft saved to data/output/fixture_verified/bulletin.md
PASS: saved output recomputed against saved source; no model call made
```

## One-command startup and shutdown

The previously running model server was stopped first. The helper then started the pinned model itself, ran all stages and saved-output verification, and terminated only its own server. Exit code: **0**.

```text
python scripts/run_demo.py --source fixture --date 2026-10-28 --output data/output/cold_start_verified
Started pinned local model on loopback.
[1/5] Acquire source=fixture
[2/5] Normalize and check geographic/time coverage
      24 hourly records; 1 interval record(s) excluded
[3/5] Calculate source-linked facts
[4/5] Run one schema-constrained local model inference
      tokens: prompt=1172 completion=24 total=1196/4096
[5/5] Validate decision and render local draft
PASS: 14 checks; draft saved to data/output/cold_start_verified/bulletin.md
PASS: saved output recomputed against saved source; no model call made
```

## Unit tests

Exit code: **0**. The explicit model-interface stub test checks integration logic and is not evidence of real model inference. Real inference is demonstrated separately above.

```text
python -m unittest discover -s tests -v
test_MET_redirect_is_allowed_and_preserves_user_agent (test_workflow.WorkflowTests.test_MET_redirect_is_allowed_and_preserves_user_agent) ... ok
test_advice_or_numbers_from_agent_rejected (test_workflow.WorkflowTests.test_advice_or_numbers_from_agent_rejected) ... ok
test_boolean_aqi_rejected (test_workflow.WorkflowTests.test_boolean_aqi_rejected) ... ok
test_changed_descriptor_boundary_rejected (test_workflow.WorkflowTests.test_changed_descriptor_boundary_rejected) ... ok
test_contact_metadata_rejected (test_workflow.WorkflowTests.test_contact_metadata_rejected) ... ok
test_descriptor_code_is_inert (test_workflow.WorkflowTests.test_descriptor_code_is_inert) ... ok
test_duplicate_decision_rejected (test_workflow.WorkflowTests.test_duplicate_decision_rejected) ... ok
test_external_redirect_is_rejected (test_workflow.WorkflowTests.test_external_redirect_is_rejected) ... ok
test_kill_switch_prevents_model_calls (test_workflow.WorkflowTests.test_kill_switch_prevents_model_calls) ... ok
test_naive_timestamp_rejected (test_workflow.WorkflowTests.test_naive_timestamp_rejected) ... ok
test_no_fallback_on_model_failure (test_workflow.WorkflowTests.test_no_fallback_on_model_failure) ... ok
test_real_inference_interface_with_explicit_test_stub (test_workflow.WorkflowTests.test_real_inference_interface_with_explicit_test_stub) ... ok
test_real_source_coverage_and_known_extrema (test_workflow.WorkflowTests.test_real_source_coverage_and_known_extrema) ... ok
test_redirect_count_is_bounded (test_workflow.WorkflowTests.test_redirect_count_is_bounded) ... ok
test_remote_model_endpoint_rejected (test_workflow.WorkflowTests.test_remote_model_endpoint_rejected) ... ok
test_render_has_exact_traceable_values_and_historical_label (test_workflow.WorkflowTests.test_render_has_exact_traceable_values_and_historical_label) ... ok
test_source_instruction_never_becomes_context (test_workflow.WorkflowTests.test_source_instruction_never_becomes_context) ... ok
test_starter_cases (test_workflow.WorkflowTests.test_starter_cases) ... ok
test_token_budget_prevents_inference (test_workflow.WorkflowTests.test_token_budget_prevents_inference) ... ok

----------------------------------------------------------------------
Ran 19 tests in 0.024s

OK
```

## Starter evaluation

Exit code: **0**. This small deterministic suite is a seed for the exam evaluation harness. Its live_model_exercised=False field is intentional; it tests acceptance and rejection logic, not language-model quality.

```text
python -m src.evaluate --output data/output/final_evaluation
PASS real_hamar_complete_day: expected=accept actual=accept
PASS fixture_missing_hour: expected=reject actual=reject
PASS fixture_wrong_region: expected=reject actual=reject
PASS nonfinite_AQI: expected=reject actual=reject
PASS duplicate_hour: expected=reject actual=reject
PASS stale_reference: expected=reject actual=reject
PASS future_reference: expected=reject actual=reject
PASS wrong_AQI_unit: expected=reject actual=reject
PASS synthetic_DST_23_hours: expected=accept actual=accept
PASS synthetic_DST_25_hours: expected=accept actual=accept
PASS synthetic_AQI_boundaries: expected=accept actual=accept
PASS corrupted_decision: expected=reject actual=reject
PASS oversized_context: expected=reject actual=reject
PASS missing_context: expected=reject actual=reject
RESULT: 14/14 cases matched expectations; live_model_exercised=False
```

## Observed failure and repair

The first live attempt failed before any model call. The source fetcher had disabled environment proxy handling. Earlier direct source probes used Python's default proxy handling and had succeeded. The fetcher was corrected to honor the environment proxy for allowlisted external MET URLs; the loopback model client still bypasses proxies. Restricted HTTPS redirects and source URL checks remain in place. The unit suite and subsequent real live run passed after this correction. This was an environment compatibility failure, not a measured MET outage.

```text
python scripts/run_demo.py --source live --date 2026-10-28 --output data/output/first_live
Reusing a healthy local model server.
[1/5] Acquire source=live
REJECTED: MET request failed or timed out; halted without retry
Exit code: 1
```

## Observed output facts

- Target date: 2026-10-28, Europe/Oslo.
- Geographic scope: Hamar municipality 3403, Innlandet 34.
- Source model reference: 2026-10-27T06:00:00Z.
- Input: 55 instantaneous hourly rows and one interval aggregate; the requested day uses 24 hourly rows.
- Peak AQI: 1.8386796712875366 at 2026-10-28T17:00:00+01:00.
- Minimum AQI: 1.6353236436843872 at 2026-10-28T00:00:00+01:00.
- All 24 requested hourly values are in source category 1, `lite`.
- Model decision: `overview`, with `coverage`, `peak`, `minimum`.
- Token use per observed model call: 1,172 prompt + 24 completion = 1,196; the reserved total cap is 4,096.
- Each pipeline run reported 14 acceptance checks, followed by successful saved-output recomputation.

## Limits of this evidence

These Linux results establish that the recorded path ran in that environment and that the stated starter tests passed. They do not establish medical usefulness, forecast accuracy, universal personal-data detection, Windows compatibility on the team's machines, comprehensive robustness, or completion of the final exam's two-class stress-testing protocol. The later Windows record has its own evidence and limits. The intended audience has not been interviewed. The source-contact detector is an extra guard; nonpersonal-data compliance primarily relies on the fixed, inspected environmental source.

## Evidence locations

This implementation repository retains four complete run bundles: the Linux [live run](evidence/live_run/), [fixture run](evidence/fixture_run/) and [cold-start run](evidence/cold_start_run/), plus the separately documented [Windows fixture run](evidence/windows_run/). Each contains saved sources, intermediates, actual prompts and responses, budgets, validation results and bulletins. The historical `evaluation.json`, `environment.json` and `run_exit_codes.json` remain under `docs/evidence/`.

The duplicate loose command/stdout/stderr text files are preserved in the original full `KIUA2003_Compulsory2_InnlandetAirBrief.zip`, outside this lean repository. Their original printed commands and results remain above. Omitting those duplicate text files here does not represent a new run or a change to the historical results.

SHA-256 values identify snapshots and help detect accidental changes; they are not digital signatures or a guarantee against coordinated tampering.
