"""Pure normalization, fact calculation, and output checks; no model or network."""
import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

FORECAST_URL = "https://api.met.no/weatherapi/airqualityforecast/0.1/?lat=60.7945&lon=11.0679&areaclass=kommune&filter_vars=AQI"
DESCRIPTOR_URL = "https://api.met.no/weatherapi/airqualityforecast/0.1/aqi_description"
LABELS = {1: "lite", 2: "moderat", 3: "høy", 4: "svært høy"}


class Rejected(ValueError):
    """Expected fail-closed rejection of unsafe or nonconforming input."""


def require(condition, message):
    if not condition:
        raise Rejected(message)


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise Rejected(f"Cannot read JSON file: {Path(path).name}") from exc


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def instant(value):
    require(isinstance(value, str), "Timestamp must be a string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Rejected("Invalid timestamp") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, "Timestamp must include UTC offset")
    return parsed.astimezone(timezone.utc)


def oslo():
    try:
        return ZoneInfo("Europe/Oslo")
    except ZoneInfoNotFoundError as exc:
        raise Rejected("Europe/Oslo timezone unavailable; install the tzdata package on Windows") from exc


def expected_hours(day):
    try:
        local_day = date.fromisoformat(day)
    except (TypeError, ValueError) as exc:
        raise Rejected("Date must be YYYY-MM-DD") from exc
    start = datetime.combine(local_day, datetime.min.time(), oslo()).astimezone(timezone.utc)
    end = datetime.combine(local_day + timedelta(days=1), datetime.min.time(), oslo()).astimezone(timezone.utc)
    return [start + timedelta(hours=i) for i in range(int((end - start).total_seconds() // 3600))]


def validate_descriptor(descriptor):
    """Read allowlisted class bounds only. Never execute the source's aqi_formula."""
    try:
        classes = descriptor["variables"]["AQI"]["aqis"]
        require(isinstance(classes, list) and len(classes) == 4, "AQI descriptor must define four classes")
        result = []
        for item, number in zip(classes, range(1, 5)):
            require(isinstance(item, dict), "Malformed AQI class")
            require(type(item["class"]) is int and item["class"] == number and item["text_NO"] == LABELS[number], "Unexpected AQI class label")
            lower = item.get("from", 1.0)
            upper = item.get("to", 5.0)
            require(lower == float(number) and upper == float(number + 1), "AQI descriptor boundaries changed")
            result.append({"class": number, "lower": lower, "upper": upper, "label_no": LABELS[number]})
        return result
    except (KeyError, TypeError, AttributeError) as exc:
        raise Rejected("Malformed AQI descriptor") from exc


def category(value, classes):
    require(type(value) in (int, float) and math.isfinite(value) and 1 <= value < 5, "AQI must be finite and in [1,5)")
    return next(c["class"] for c in classes if c["lower"] <= value < c["upper"])


def normalize(raw, descriptor, day, as_of):
    classes = validate_descriptor(descriptor)
    as_of = instant(as_of)
    wanted = expected_hours(day)
    try:
        meta = raw["meta"]
        location = meta["location"]
        require(location["areacode"] == "3403" and location["name"] == "Hamar", "Only Hamar municipality 3403 is supported")
        require(location["areaclass"] == "kommune" and location["superareacode"] == "34", "Wrong geographic scope")
        require(meta["superlocation"]["name"] == "Innlandet" and meta["superlocation"]["areacode"] == "34", "Wrong county")
        reference = instant(meta["reftime"])
        age = (as_of - reference).total_seconds()
        require(0 <= age <= 48 * 3600, "Forecast reference is future-dated or older than 48 hours")
        source_rows = raw["data"]["time"]
        require(isinstance(source_rows, list) and 1 <= len(source_rows) <= 500, "Unexpected number of source records")
        rows, seen, ignored_intervals = [], set(), 0
        for index, row in enumerate(source_rows):
            start, end = instant(row["from"]), instant(row["to"])
            require(end >= start, "Invalid reversed forecast interval")
            if start != end:
                ignored_intervals += 1
                continue
            require(start not in seen, "Duplicate hourly forecast timestamp")
            seen.add(start)
            require(start.minute == start.second == start.microsecond == 0, "Hourly timestamps must be on the hour")
            item = row["variables"]["AQI"]
            require(item["units"] == "1", "AQI must have dimensionless unit 1")
            value = item["value"]
            level = category(value, classes)
            if start in wanted:
                rows.append({"source_row": index, "time_utc": start.isoformat(), "time_local": start.astimezone(oslo()).isoformat(), "aqi": value, "class": level, "category_no": LABELS[level]})
        rows.sort(key=lambda row: row["time_utc"])
        require([instant(row["time_utc"]) for row in rows] == wanted, f"Incomplete local day: expected {len(wanted)} distinct hourly forecasts")
        return {"location": "Hamar", "municipality_code": "3403", "county": "Innlandet", "date": day, "timezone": "Europe/Oslo", "as_of": as_of.isoformat(), "reference_time": reference.isoformat(), "hours_expected": len(wanted), "interval_rows_ignored": ignored_intervals, "source_url": FORECAST_URL, "classes": classes, "hours": rows}
    except (KeyError, TypeError, AttributeError) as exc:
        raise Rejected("Malformed forecast structure") from exc


def build_facts(normalized):
    rows = normalized["hours"]
    peak = max(rows, key=lambda row: row["aqi"])
    minimum = min(rows, key=lambda row: row["aqi"])
    counts = {str(number): sum(row["class"] == number for row in rows) for number in LABELS}
    return {
        "date": normalized["date"], "location": "Hamar", "reference_time": normalized["reference_time"],
        "facts": {
            "coverage": {"hours": len(rows), "first": rows[0]["time_local"], "last": rows[-1]["time_local"], "source_rows": [row["source_row"] for row in rows]},
            "peak": dict(peak), "minimum": dict(minimum),
            "distribution": {"hour_counts": counts, "source_rows": [row["source_row"] for row in rows]},
        },
        "tie_rule": "earliest timestamp wins", "numeric_policy": "Full precision in facts; three decimals in text; classes use unrounded values.",
    }


def validate_decision(decision, facts, schema):
    require(isinstance(decision, dict) and set(decision) == {"opening", "fact_ids"}, "Decision has wrong fields")
    require(decision["opening"] in ("overview", "timing"), "Invalid opening style")
    ids = decision["fact_ids"]
    require(isinstance(ids, list) and len(ids) == 3 and all(isinstance(i, str) for i in ids), "Exactly three fact IDs required")
    require(len(set(ids)) == 3 and {"peak", "coverage"}.issubset(ids), "Decision must contain distinct coverage and peak facts")
    require(all(i in facts["facts"] for i in ids), "Unknown fact ID")
    require(ids in schema["properties"]["fact_ids"]["enum"], "Decision violates loaded schema")
    return {"passed": True, "checks": ["exact_decision_fields", "allowed_opening", "three_distinct_fact_ids", "required_peak_and_coverage", "all_fact_references_exist", "loaded_schema_conformance"]}


def render(decision, facts, normalized, source_mode):
    def value_text(value):
        return f"{value:.3f}".replace(".", ",")
    def phrase(fact_id):
        f = facts["facts"][fact_id]
        if fact_id == "coverage":
            return f"Datagrunnlaget dekker {f['hours']} timer, fra {f['first']} til {f['last']} (Europe/Oslo)."
        if fact_id in ("peak", "minimum"):
            word = "Høyeste" if fact_id == "peak" else "Laveste"
            return f"{word} varslede AQI er {value_text(f['aqi'])} ved {f['time_local']}, kategori «{f['category_no']}»."
        counts = f["hour_counts"]
        return "Varslede timer per kategori: " + "; ".join(f"{LABELS[i]}: {counts[str(i)]}" for i in LABELS) + "."
    lead = "Her er en kort oversikt over luftkvalitetsvarselet." if decision["opening"] == "overview" else "Her er tidspunkter og dekning i luftkvalitetsvarselet."
    bullets = [{"fact_id": i, "text": phrase(i), "evidence": facts["facts"][i]} for i in decision["fact_ids"]]
    result = {"title": f"Luftkvalitetsvarsel for Hamar – {facts['date']}", "municipality_code": normalized["municipality_code"], "county_code": "34", "target_date": normalized["date"], "timezone": normalized["timezone"], "hours_expected": normalized["hours_expected"], "status": "draft_requires_human_review", "source_mode": source_mode, "as_of": normalized["as_of"], "reference_time": normalized["reference_time"], "opening": lead, "items": bullets, "source_url": FORECAST_URL, "attribution": "Data fra MET Norway, CC BY 4.0. Bearbeidet og forkortet.", "limitations": ["Dette er et modellberegnet varsel, ikke målinger.", "Kommunedata beskriver ikke nødvendigvis luften på et bestemt sted.", "AQI vises med tre desimaler; kategori er beregnet fra uavrundet verdi.", "Dette utkastet gir ingen individuelle helseråd."]}
    if source_mode == "fixture":
        result["limitations"].insert(0, "Historisk eksempel fra en lagret kildefil; ikke et oppdatert varsel.")
    markdown = f"# {result['title']}\n\n**Utkast – må gjennomgås av et menneske.**\n\n{lead}\n\n"
    markdown += "\n".join("- " + item["text"] for item in bullets)
    markdown += f"\n\nModellens referansetid: {normalized['reference_time']}.\n\n" + "\n".join(result["limitations"])
    markdown += f"\n\n{result['attribution']} [Kilde]({FORECAST_URL}) · [Lisens](https://creativecommons.org/licenses/by/4.0/)\n"
    return result, markdown
