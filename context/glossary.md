# Bounded glossary
Purpose: explain the four allowed facts and preserve forecast terminology.

AQI is the dimensionless air-quality index supplied by MET Norway. This workflow
describes a model forecast for Hamar municipality, not a measurement or a personal
exposure estimate. The time zone is Europe/Oslo. Facts refer to one complete local
calendar day. Values retain source precision; display rounding is deterministic.

coverage: the number and first/last timestamps of hourly records for the day.
peak: greatest forecast AQI and its earliest timestamp if tied.
minimum: least forecast AQI and its earliest timestamp if tied.
distribution: hourly counts in each of four source-defined pollution categories.

The schema defines the output contract. example.json is a format example only.
Do not copy example choices without considering the provided facts.
