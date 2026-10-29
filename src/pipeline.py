"""CLI: one command executes the complete workflow, requiring a real local model."""
import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from .agent import decide
from .core import Rejected, build_facts, normalize, render, require, sha256, validate_decision, write_json
from .fetch import acquire

ROOT = Path(__file__).resolve().parent.parent


def run(args):
    require(os.environ.get("AIRBRIEF_STOP") != "1", "AIRBRIEF_STOP kill switch is active")
    if args.source == "fixture":
        require(args.as_of is not None, "Historical fixture mode requires explicit --as-of timestamp")
        as_of = args.as_of
    else:
        require(args.as_of is None, "Live mode uses the actual clock; --as-of is forbidden")
        as_of = datetime.now(timezone.utc).isoformat()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    require(not any(output.iterdir()), "Output directory must be empty; choose a fresh run directory")
    print(f"[1/5] Acquire source={args.source}", flush=True)
    raw, descriptor, manifest = acquire(args.source, ROOT / "data/fixtures", ROOT / "data/cache")
    write_json(output / "raw_forecast.json", raw)
    write_json(output / "raw_descriptor.json", descriptor)
    manifest.update({"requested_date": args.date, "as_of": as_of})
    manifest["saved_artifact_sha256"] = {name: sha256((output / name).read_bytes()) for name in ("raw_forecast.json", "raw_descriptor.json")}
    write_json(output / "source_manifest.json", manifest)
    print("[2/5] Normalize and check geographic/time coverage", flush=True)
    normalized = normalize(raw, descriptor, args.date, as_of)
    write_json(output / "normalized.json", normalized)
    print(f"      {len(normalized['hours'])} hourly records; {normalized['interval_rows_ignored']} interval record(s) excluded", flush=True)
    print("[3/5] Calculate source-linked facts", flush=True)
    facts = build_facts(normalized)
    write_json(output / "facts.json", facts)
    print("[4/5] Run one schema-constrained local model inference", flush=True)
    decision, schema, budget = decide(facts, Path(args.context_dir), output)
    write_json(output / "decision.json", decision)
    write_json(output / "decision_schema.json", schema)
    print(f"      tokens: prompt={budget['prompt_tokens']} completion={budget['completion_tokens']} total={budget['total_tokens']}/{budget['total_tokens_max']}", flush=True)
    print("[5/5] Validate decision and render local draft", flush=True)
    validation = validate_decision(decision, facts, schema)
    validation["checks"] = ["Hamar_3403_Innlandet_34", "reference_age_0_to_48h", "complete_local_calendar_day", "distinct_hourly_timestamps", "finite_AQI_and_units", "official_descriptor_boundaries", "source_linked_recomputed_facts", "enforced_one_call_token_budget"] + validation["checks"]
    validation["hour_count"] = len(normalized["hours"])
    bulletin, markdown = render(decision, facts, normalized, args.source)
    write_json(output / "bulletin.json", bulletin)
    (output / "bulletin.md").write_text(markdown, encoding="utf-8")
    write_json(output / "validation.json", validation)
    print(f"PASS: {len(validation['checks'])} checks; draft saved to {output / 'bulletin.md'}", flush=True)
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("fixture", "live"), required=True)
    parser.add_argument("--date", required=True, help="Europe/Oslo calendar date YYYY-MM-DD")
    parser.add_argument("--as-of", help="Explicit historical clock for fixture mode only")
    parser.add_argument("--output", default="data/output/run", help="New or empty directory")
    parser.add_argument("--context-dir", default=str(ROOT / "context"))
    args = parser.parse_args()
    try:
        return run(args)
    except (Rejected, OSError) as exc:
        print(f"REJECTED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
