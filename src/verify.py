"""Recompute a saved output from its saved source, without model or network."""
import argparse
from pathlib import Path

from .core import Rejected, build_facts, load_json, normalize, render, require, sha256, validate_decision


def verify(directory):
    directory = Path(directory)
    manifest = load_json(directory / "source_manifest.json")
    for name in ("raw_forecast.json", "raw_descriptor.json"):
        require(sha256((directory / name).read_bytes()) == manifest["saved_artifact_sha256"][name], "Saved source artifact hash mismatch")
    normalized = normalize(load_json(directory / "raw_forecast.json"), load_json(directory / "raw_descriptor.json"), manifest["requested_date"], manifest["as_of"])
    require(normalized == load_json(directory / "normalized.json"), "Saved normalization differs from source")
    facts = build_facts(normalized)
    require(facts == load_json(directory / "facts.json"), "Saved facts differ from source calculations")
    decision = load_json(directory / "decision.json")
    validate_decision(decision, facts, load_json(directory / "decision_schema.json"))
    expected, text = render(decision, facts, normalized, manifest["mode"])
    require(expected == load_json(directory / "bulletin.json"), "Bulletin JSON differs from validated facts")
    require(text == (directory / "bulletin.md").read_text(encoding="utf-8"), "Bulletin text differs from validated facts")
    budget = load_json(directory / "budget.json")
    require(budget.get("generation_calls_used") == 1 and budget.get("within_cap") is True and budget.get("total_tokens", 99999) <= 4096, "Saved budget check failed")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        verify(args.output)
        print("PASS: saved output recomputed against saved source; no model call made")
        return 0
    except (Rejected, OSError, KeyError, TypeError, AttributeError) as exc:
        print(f"REJECTED: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
