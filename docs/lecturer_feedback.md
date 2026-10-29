# Lecturer correspondence and C2 decision

**Recorded:** 29 October 2026.  
**Provenance:** substantive correspondence text supplied by the user in this
conversation. The original email was not independently accessed. Its original
send/receive timestamps are unknown; the recording date is not an inferred email
date. Greetings and sign-offs are omitted, so these are substantive excerpts,
not complete emails. No email addresses or message headers are reproduced.

## Student question to the lecturer

The following text is reproduced as supplied, without grammatical correction:

> Our C2 project is a five-stage pipeline, it fetches MET air-quality forecasts for Hamar, normalize and validate in Python, compute facts, run one local LLM call, then validate and render a Norwegian bulletin. Python computes all facts. The LLM only chooses which facts to emphasize and in what order, and the checks are mechanical.
>
> Does this satisfy the "agent step" in the walking skeleton, or do you expect the run-time model to use tools in a loop (as in the agent loop on the W40 slides)? If a more active role is expected, we will make sure its in the whitepaper

## Lecturer reply

The following text is reproduced as supplied:

> The skeleton seems fine. But I recommend you to think more about the impact of your method to the Innlandet fylke, beyond the technical stuff. How do you connect this idea to address a key problem of the county? I will be equally interested in this.

## Subsequent user direction

The user's project choice in this conversation was:

> okay so we will deliver the air thing for comp2 then

The user subsequently clarified the timing of a possible change:

> which we might do for the whitepaper, but not currently for the comp2

These statements settle retaining Air Brief for C2. A possible later change for
the white paper remains an option for review, with no replacement project
selected, implemented or treated as approved by the lecturer.

## Interpretation and response

The supplied reply expresses that the skeleton seems acceptable and directs
attention to regional impact. It does not request an additional model tool loop
or constitute a formal C2 pass. The immediate response is to strengthen the
existing project's problem statement and evaluation plan while retaining its
five-stage implementation and mechanical definition of success.

The proposed task is a dated environmental-information update prepared by Hamar
information staff or activity organisers. [Official local evidence](impact_sources.md)
supports a bounded Hamar context and a county connection. It does not establish
that an institution wants this tool or that air pollution is a general Innlandet
crisis. The possible benefit is less transcription and easier checking of place,
forecast issue time, coverage and source. A planned comparison of manual,
fixed-template and model-assisted preparation will investigate that hypothesis.
No interview, measured time saving, improved health or institutional adoption is
claimed.

Historical alternatives and tradeoff research are preserved in the original full
C2 package outside this implementation repository. The
[decision record](decision_record.md) records the project choice and later KEEP decision.
The [prompt log](prompt_log.md) includes this exchange as part of the real
feedback and revision history.

## Evidence boundary and outstanding work

This document is correspondence and decision evidence. It is not a team-meeting
report and does not establish attendance, a meeting date, a stakeholder interview
or completed substantive review by both students. The user has reported
approximately five student meetings; their actual dates, attendance and contents
remain to be confirmed for the separate report submission. Repository URL/access
and submission details also remain outstanding. The later supplied
Windows fixture-run transcript and 14 run files are recorded in
[windows_run_20261029.md](windows_run_20261029.md). Their saved-source output
passed independent recomputation with `src.verify` on Linux (exit code 0); see
the [artifact review](windows_evidence/20261029/artifact_review/). That review
made no new model call and establishes neither a new Windows model execution
nor a Windows live MET fetch. The exact Windows build and original run timestamp
remain unestablished. The supplied Windows total of 1,195 tokens remains distinct
from the historical Linux total of 1,196.

The imported repository evidence retains the actual GGUF basename in
`agent_response.json` while removing its user-profile directory; 13 other files
remain byte-identical. The
[import manifest](windows_evidence/20261029/artifact_import.json) records original
and packaged hashes and the one-field redaction.

Any later domain change would require its own decision, appropriate scope
discussion, new domain checks/context/fixtures and fresh execution evidence.
Historical Air Brief results must not be relabelled as results of another project.
