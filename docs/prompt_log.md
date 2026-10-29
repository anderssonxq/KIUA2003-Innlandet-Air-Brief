# Representative prompt log

**Scope:** Real excerpts from this conversation. Quotation text is preserved; explanations outside quotations are annotations. This file is a short selection for the report appendix, not a complete conversation export. The report appendix must keep prompt-log excerpts to at most two pages.

## 1. User sets verification responsibility before implementation

**Speaker:** User. **Timing:** Initial three-phase project instruction, before project code.

> Do not claim it works unless you ran it.

> Paste the real command output into docs/first_run.md.

**Effect on work:** A planned pipeline or replay was not accepted as proof of a real run. The implementation must capture its actual command and observed result. This is an explicit user constraint, not a fabricated report that the student later rejected a specific code change.

## 2. User requires a genuine source and rejects fabrication

**Speaker:** User. **Timing:** Initial three-phase project instruction.

> Do not fabricate: no invented citations, APIs, library functions, URLs, or
>    tool capabilities. If you are unsure something exists, verify it (run it,
>    read docs, or search) or say so explicitly.

**Effect on work:** Candidate endpoints and permission documents were checked, and actual data requests were made before selection. The retained `source_verification.md` documents the selected MET source. Broader historical candidate research is preserved in the original full C2 package outside this implementation repository. These checks are assistant verification, not a claimed student review or team-meeting decision.

## 3. User protects the integrity of meeting evidence

**Speaker:** User. **Timing:** Report requirements.

> DO NOT invent meetings, dates, attendees,
>   or decisions that did not happen.

**Effect on work:** Planned schedule slots were labelled as plans, not completed events. The user later reported approximately five student meetings; their actual dates, attendance and contents remain to be confirmed by the team. Genuine meeting reports belong with the separate report submission. This prompt log does not establish those meeting details, and blank meeting templates are not included in this implementation repository.

## 4. User defines the report-template boundary

**Speaker:** User. **Timing:** Report requirements.

> If I have not provided neurips_2025.sty, say so and structure the .tex so it
>   compiles once I drop the provided template files in. Do not fabricate the
>   style file.

**Effect on work:** No replacement style file should be invented. The original assignment PDF contained the official NeurIPS style-package URL; the root assistant retrieved that actual package. Report, template and compilation records are retained outside this implementation repository.

## 5. Assistant commits to separating observed results from plans

**Speaker:** Assistant. **Timing:** First response to the three-phase instruction.

> I’ll work through the three phases in order: compare and verify the project options, build and run the selected skeleton, then compile the report and check its length.

> I’ll keep verified results separate from planned work, especially for model access, source permissions, and meeting records.

**Effect on work:** Source research preceded the decision and project code. The decision is labelled as an engineering decision within the assistant session, not a team approval. Actual execution and compilation must be supported by logs.

## 6. Observed integration failure corrected during engineering review

**Speaker:** Assistant. **Timing:** After the first real live-source attempt.

> The saved-source run passed with real local inference. The first live-source run stopped at the fetch stage. I found that the fetcher bypassed this environment’s configured network proxy; the earlier source checks had succeeded using that proxy.

**Observed correction:** External MET requests were changed to honor the environment proxy while retaining source and redirect restrictions. The loopback model client still bypasses proxies. The real live run then passed. See `first_run.md` for the unedited failure and success output. This is assistant engineering review, not a claimed student rejection or meeting decision.

## Human correction/rejection evidence at the initial 27 October delivery

At this initial delivery, the visible conversation contains detailed user constraints, but **no later student turn reviewing and rejecting a specific generated code or report result**. The excerpts above must not be relabelled as such. Assistant self-review is also not a substitute for student judgment.

At that stage, the team was asked to review the code, checks and prose and retain genuine exchanges showing corrections, challenges or rejections. The later question, feedback and Windows setup correction are recorded below; they must not be backdated or presented as completed substantive review by both students.

## 7. User supplies lecturer feedback and retains Air for C2 — recorded 29 October 2026

**Provenance:** the user supplied the substantive correspondence excerpts below
in this conversation. The underlying email was not independently accessed and
its original send/receive timestamps are unknown. The recording date is not an
inferred email date. Greetings and sign-offs are omitted; these are substantive
excerpts, not complete emails. This is feedback evidence, not a team-meeting report.

**Student question to the lecturer, as supplied by the user:**

> Our C2 project is a five-stage pipeline, it fetches MET air-quality forecasts for Hamar, normalize and validate in Python, compute facts, run one local LLM call, then validate and render a Norwegian bulletin. Python computes all facts. The LLM only chooses which facts to emphasize and in what order, and the checks are mechanical.
>
> Does this satisfy the "agent step" in the walking skeleton, or do you expect the run-time model to use tools in a loop (as in the agent loop on the W40 slides)? If a more active role is expected, we will make sure its in the whitepaper

**Lecturer reply, as supplied by the user:**

> The skeleton seems fine. But I recommend you to think more about the impact of your method to the Innlandet fylke, beyond the technical stuff. How do you connect this idea to address a key problem of the county? I will be equally interested in this.

**User's C2 decision in this conversation:**

> okay so we will deliver the air thing for comp2 then

**User's later clarification:**

> which we might do for the whitepaper, but not currently for the comp2

**Effect on the work:** retain the existing Air Brief implementation for C2 and
revise the report/specification's local rationale and proposed usefulness
evaluation. The feedback challenged the emphasis on technical correctness; the
response is to define a concrete dated-information task, cite appropriate local
context and distinguish possible benefit from demonstrated benefit. A possible
later pivot remains open, with no replacement selected or implemented.

The supplied reply does not require adding a model tool loop and does not award
a formal C2 pass. Neither the lecturer correspondence nor the user's KEEP
instruction establishes a meeting, stakeholder interview, measured time saving,
health improvement or completed review by both students. The full evidence
distinction is recorded in [lecturer_feedback.md](lecturer_feedback.md), and the
dated decision continuation is in [decision_record.md](decision_record.md).

## 8. User reports a Windows setup issue and successful reproduction — recorded 29 October 2026

**User-supplied error from the initial PowerShell attempt:**

> ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'

**Assistant correction:**

> You're one folder above the actual project.

The assistant's original sentence used a typographic apostrophe and bold emphasis;
the excerpt above normalises that typography. The concrete instruction was to
enter `innlandet-air-brief` before creating the virtual environment and installing
requirements. The README now makes that extraction step explicit.

**Subsequent user-supplied results:**

> tokens: prompt=1172 completion=23 total=1195/4096

> PASS: 14 checks; draft saved to data\output\windows01\bulletin.md

> PASS: saved output recomputed against saved source; no model call made

These are supplied terminal excerpts, not commands executed by the assistant on
the user's computer. The complete retained transcript and its provenance are in
[windows_run_20261029.md](windows_run_20261029.md). The user subsequently uploaded
the 14 original run files; these passed independent saved-output verification on
Linux. The repository copy documents one local-profile-path redaction. This is
reproduction and documentation-correction evidence, not a meeting report or proof
of review by both students.

## Current review status

The later feedback and KEEP direction now provide a real continuation of the
initial prompt history. Both students still need to review and understand the
code, sources, checks and final report. Preserve further consequential reviews
only when they occur, and keep the report's selected prompt excerpts within the
two-page limit. The full Markdown log is supporting material, not a claim that
all of it appears in the report appendix.
