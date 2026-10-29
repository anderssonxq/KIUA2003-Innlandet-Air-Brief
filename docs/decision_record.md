# Decision record: Innlandet Air Brief for Compulsory 2

## Initial recommendation

The original engineering selection was recorded on 27 October 2026 after
comparing candidate workflows and checking sources. Air Brief was recommended
because its official municipal forecast is a recurring, nonpersonal input and
its location, time coverage and calculated values can be checked mechanically.
The selected-source observations are retained in
[source_verification.md](source_verification.md).

This was a recommendation during assistant-supported development, not a
fabricated student meeting or stakeholder endorsement. The broader candidate
comparison and unused pivot research are preserved in the original full project
package, outside this cleaned implementation repository.

## Scope and tradeoffs

Keep one municipality: Hamar (3403), in Innlandet (34). Produce a Norwegian local
draft with source provenance, a computed fact ledger and deterministic checks.
Python computes and renders facts. One bounded local-model call selects and
orders permitted fact identifiers.

This scope gives up broad geographic coverage, personalisation, automatic
publication and unrestricted model prose. The proposed benefit is less manual
transcription and easier verification for someone preparing a dated Hamar
environmental update. It is a hypothesis; demand, time savings, improved health
and institutional adoption have not been demonstrated. The
[local source record](impact_sources.md) and
[specification](../SPEC.md) explain the limits.

## Continuation recorded 29 October 2026

The user explicitly selected the existing Air Brief project for C2:

> okay so we will deliver the air thing for comp2 then

The later clarification kept a possible white-paper change separate:

> which we might do for the whitepaper, but not currently for the comp2

The supplied lecturer reply said the skeleton seemed fine and asked for a
stronger connection to Innlandet's needs. The response was to retain the working
pipeline and strengthen the local problem statement and proposed usefulness
comparison. The [correspondence record](lecturer_feedback.md) preserves the
substantive question and reply.

This is a recorded user instruction, not evidence of a team meeting, formal
assessment pass or approval of a particular future pivot. A later domain change
would need its own justification, domain checks, context, fixtures and new
end-to-end evidence.

## Technical checkpoint and acceptance boundary

The original technical checkpoint was 29 October 2026 at 18:00 Europe/Oslo:
reconsider the fallback if a valid complete source day or a real-model path
remained unavailable after a bounded repair attempt. The recorded Linux runs
establish that path; the supplied Windows fixture artifacts also passed
saved-output verification. Reaching the checkpoint does not require abandoning
a working skeleton.

Redesign if source permissions conflict with the task or the required workflow
introduces identifying data. Do not weaken acceptance checks to obtain a pass.
Outputs remain local drafts for review.

## Evidence and remaining responsibilities

- [First executed runs](first_run.md): live, fixture and automatic-startup Linux
  records, the observed fetch failure/repair, and starter-test results.
- [Windows reproduction](windows_run_20261029.md): supplied fixture run, distinct
  token count, independent artifact checks and documented path redaction.
- [Prompt log](prompt_log.md): original instructions and consequential corrections.
- [Planned usefulness comparison](../SPEC.md#planned-usefulness-evaluation):
  manual, fixed-template and model-assisted preparation on identical snapshots.

The report, its prompt appendix and actual meeting reports are maintained
separately in Overleaf. The team must provide the real repository link in that
report, check assessor access and review the final work. These records do not
claim that a repository has already been published or that both students have
completed their review.
