# MET source and reuse record

This file retains the selected Air Brief source checks from the original
feasibility work on 27 October 2026. It records historical observations; it does
not claim a new request during repository cleanup or guarantee future availability.
Broader candidate research remains in the original full project package.

The source snapshots required by fixture mode are in `data/fixtures/`. Their
manifest records byte hashes and provenance. The complete actual live-run
artifacts are in [evidence/live_run/](evidence/live_run/), and the executed
commands and observed results are in [first_run.md](first_run.md).

## Selected source: MET Airqualityforecast

Primary documentation and terms:

- <https://api.met.no/weatherapi/airqualityforecast/0.1/documentation>
- <https://api.met.no/doc/TermsOfService>
- <https://api.met.no/doc/License>
- <https://www.met.no/en/free-meteorological-data/Licensing-and-crediting>

Exact selected data request:

```text
https://api.met.no/weatherapi/airqualityforecast/0.1/?lat=60.7945&lon=11.0679&areaclass=kommune&filter_vars=AQI
```

The root reviewer independently repeated this fetch before choosing the project. Observed response:

```text
HTTP status: 200
Content-Type: application/json
Bytes: 10773
HTTP Date: Tue, 27 Oct 2026 16:25:25 GMT
Expires: Tue, 27 Oct 2026 16:31:44 GMT
Last-Modified: Tue, 27 Oct 2026 16:25:25 GMT
SHA-256: e588f353fb2fe62a485bd0baa1d4f080c5619b1d3cfd7b3728d7454e40601666
Location: Innlandet/Hamar
Municipality code: 3403
Area class: kommune
Requested variables: AQI
Total records: 56
Instantaneous records (from == to): 55
Forecast reference time: 2026-10-27T06:00:00Z
```

One observed instantaneous record was:

```json
{"from":"2026-10-27T12:00:00Z","to":"2026-10-27T12:00:00Z","variables":{"AQI":{"value":1.608568549156189,"units":"1"}},"reason":{"variables":[],"sources":[]}}
```

The additional interval record must not count as an extra forecast hour. The exact day selected by the implementation must be derived and checked from the available records; the presence of 55 instantaneous records alone does not prove coverage for every local calendar day.

Official descriptors were also fetched from:

```text
https://api.met.no/weatherapi/airqualityforecast/0.1/aqi_description
```

The descriptor request returned HTTP 200 and 26,068 bytes. The official category semantics are the source for labels and meanings. They do not authorize personalized medical recommendations.

**Terms and conditions applied:** MET's open-data licensing policy provides a reuse basis under CC BY 4.0/NLOD. Credit MET Norway, link to the source and license, and make transformations clear. Do not imply endorsement. The service terms require truthful application identification and restrained traffic. They recommend operator contact information; the project must not invent a contact address or repository URL. Use HTTPS, support normal response handling, cache, and respect expiry/conditional-request instructions. A successful request does not itself prove continued compliance.

**Privacy finding:** The inspected selected response contains environmental forecast values and fixed public municipality metadata, not personal identities. This remains a per-run schema constraint; do not broaden the requested fields without review.

## Application rules

- Keep the fixed municipal geography and limited environmental variables.
- Identify the application truthfully. Once the repository exists, use its real
  URL in `MET_USER_AGENT`; do not invent a contact address.
- Retain source, licence, transformation and historical-fixture labels in output.
- Respect expiry and conditional requests. The implementation bounds responses
  and timeouts and does not run an automatic retry loop.
- Treat descriptor formulas as untrusted data; do not execute them.
- Recheck terms and privacy before changing the source or requested fields.

The [specification](../SPEC.md) defines the implemented acceptance checks.
Runtime and model download provenance is retained in
[scripts/setup_runtime.py](../scripts/setup_runtime.py) and the README.
