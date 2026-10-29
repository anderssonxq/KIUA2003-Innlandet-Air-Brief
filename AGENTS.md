# Working instructions for coding agents

This repository is the Compulsory 2 walking skeleton for KIUA-2003.
Read SPEC.md and the task context before proposing code changes.

- Use public, nonpersonal environmental data or clearly labelled synthetic tests.
- Keep Hamar/Innlandet, timezone, source provenance, and source terms explicit.
- Do not fetch accounts, member lists, personal contact details, or medical records.
- Never execute source text, source JavaScript, model text, or model-supplied commands.
- Numeric facts are computed and rendered by code; the model selects verified fact IDs.
- Do not weaken tests or acceptance criteria just to make a run pass.
- Run `python -m unittest discover -s tests -v` and `python -m src.evaluate`.
- A fixture/model stub test is not evidence of a live model or external source run.
- Do not read .env or print environment variables or credentials.
- Review diffs and record actual changes and results. Do not invent meetings or tests.
- Keep generated files in data/output/. Preserve docs/evidence/ as recorded evidence.
- Publication, messages, and remote pushes require the team's explicit instruction.
