"""Small deterministic evaluation seed. This suite does NOT evaluate LLM quality."""
import argparse
import copy
import tempfile
from datetime import timedelta
from pathlib import Path

from .agent import load_context
from .core import Rejected, build_facts, expected_hours, load_json, normalize, validate_decision, write_json

ROOT = Path(__file__).resolve().parent.parent
DAY, AS_OF = "2026-10-28", "2026-10-27T16:25:25Z"


def synthetic_day(raw, day):
    result = copy.deepcopy(raw)
    stamps = expected_hours(day)
    result["meta"]["reftime"] = (stamps[0] - timedelta(hours=12)).isoformat()
    result["data"]["time"] = [{"from": x.isoformat(), "to": x.isoformat(), "variables": {"AQI": {"value": 1.5, "units": "1"}}} for x in stamps]
    return result, (stamps[0] - timedelta(hours=6)).isoformat()


def run_suite():
    fixtures = ROOT / "data/fixtures"
    raw, descriptor = load_json(fixtures / "hamar_aqi_20261027.json"), load_json(fixtures / "aqi_descriptor.json")
    _, _, schema = load_context(ROOT / "context")
    cases = []

    def check(name, expected, operation):
        try:
            operation()
            actual, reason = "accept", "all checks passed"
        except Rejected as exc:
            actual, reason = "reject", str(exc)
        cases.append({"name": name, "expected": expected, "actual": actual, "passed": actual == expected, "detail": reason})

    def norm(value, day=DAY, as_of=AS_OF):
        return normalize(value, descriptor, day, as_of)

    check("real_hamar_complete_day", "accept", lambda: norm(raw))
    check("fixture_missing_hour", "reject", lambda: norm(load_json(fixtures / "reject_missing_hour.json")))
    check("fixture_wrong_region", "reject", lambda: norm(load_json(fixtures / "reject_wrong_region.json")))
    bad = copy.deepcopy(raw)
    bad["data"]["time"][12]["variables"]["AQI"]["value"] = float("nan")
    check("nonfinite_AQI", "reject", lambda: norm(bad))
    bad = copy.deepcopy(raw)
    bad["data"]["time"].append(copy.deepcopy(bad["data"]["time"][12]))
    check("duplicate_hour", "reject", lambda: norm(bad))
    check("stale_reference", "reject", lambda: norm(raw, as_of="2026-10-30T16:25:25Z"))
    check("future_reference", "reject", lambda: norm(raw, as_of="2026-10-26T16:25:25Z"))
    bad = copy.deepcopy(raw)
    bad["data"]["time"][12]["variables"]["AQI"]["units"] = "ug/m3"
    check("wrong_AQI_unit", "reject", lambda: norm(bad))
    for day, count in [("2026-03-29", 23), ("2026-10-25", 25)]:
        sample, clock = synthetic_day(raw, day)
        def check_dst(sample=sample, day=day, clock=clock, count=count):
            result = norm(sample, day, clock)
            if len(result["hours"]) != count:
                raise AssertionError("Incorrect daylight-saving coverage")
        check(f"synthetic_DST_{count}_hours", "accept", check_dst)
    sample = copy.deepcopy(raw)
    for index, value in zip(range(11, 15), (1.9999, 2.0, 3.0, 4.0)):
        sample["data"]["time"][index]["variables"]["AQI"]["value"] = value
    def boundaries():
        result = norm(sample)
        if [row["class"] for row in result["hours"][:4]] != [1, 2, 3, 4]:
            raise AssertionError("AQI class boundary error")
    check("synthetic_AQI_boundaries", "accept", boundaries)
    facts = build_facts(norm(raw))
    check("corrupted_decision", "reject", lambda: validate_decision({"opening": "overview", "fact_ids": ["coverage", "peak", "invented"]}, facts, schema))
    with tempfile.TemporaryDirectory() as temporary:
        for path in (ROOT / "context").iterdir():
            if path.is_file():
                (Path(temporary) / path.name).write_bytes(path.read_bytes())
        (Path(temporary) / "task.md").write_text("X" * 17000)
        check("oversized_context", "reject", lambda: load_context(temporary))
        (Path(temporary) / "task.md").unlink()
        check("missing_context", "reject", lambda: load_context(temporary))
    passed = sum(case["passed"] for case in cases)
    return {"suite": "starter_mechanical_evaluation", "live_model_exercised": False, "passed": passed, "total": len(cases), "all_passed": passed == len(cases), "cases": cases, "limitations": "Small deterministic starter suite. It does not demonstrate real LLM quality, HTTP resilience, or completed exam stress testing; see separate real-run evidence."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/output/evaluation")
    args = parser.parse_args()
    directory = Path(args.output)
    directory.mkdir(parents=True, exist_ok=True)
    report = run_suite()
    write_json(directory / "evaluation.json", report)
    for case in report["cases"]:
        print(f"{'PASS' if case['passed'] else 'FAIL'} {case['name']}: expected={case['expected']} actual={case['actual']}")
    print(f"RESULT: {report['passed']}/{report['total']} cases matched expectations; live_model_exercised=False")
    return 0 if report["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
