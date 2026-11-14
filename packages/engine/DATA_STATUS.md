# Crop database coverage and research limits — Rootwise M1 v0.2

The reference crop database is **source-labelled**. It is not a farm dataset.
Below, `proxy` means a class/variety- or region-transfer rather than an
observation made for the selected crop cultivar in Devanahalli.

| Crop | Seasonal reference ET (mm) | Reference basis | Forage crude protein (% dry matter) | Feed material | Five-stage crop phase fully verified? |
|---|---:|---|---:|---|---|
| Ragi | 450–650 | FAO generic millet | 5.0 | straw | No |
| Groundnut | 500–700 | FAO peanut | 11.1 | dry haulms | No |
| Horse gram | **unknown** | No transferable ETc reference | **unknown** | herbage | No |
| Cowpea | 300–500 | FAO generic dry bean | 13.7 | haulms | No |
| Pigeon pea | 500–800 | ICRISAT Table 10.7, FAO attribution | 14.5 | hay, n=2 | No |
| Green gram | 350–400 | ICRISAT generic green/black gram table | 9.8 | straw | No |
| Sorghum | 450–650 | FAO sorghum/millet | 3.7 | straw | No |
| Foxtail millet | 450–650 | FAO generic millet | 4.2 | stover | No |

**Crude protein is only forage *quality*, not total forage quantity.** It does not
establish digestibility, animal diet safety or the forage yield per hectare.

## Delivered by M1 in this release

- Eight crops, source audit, multiple UAS/TNAU variety references, published
  water-use and forage material references where supported.
- Six implemented, testable scoring methods and normalized criteria with
  explicit policy benchmarks and missingness handling.
- Three distinct ranked focus options; each displayed score uses the farmer's
  selected weights. A tie is not evidence of superiority.
- Crop phase, evidence, confidence, vulnerability threshold flags, observed bare
  field episodes, crop ETc with daily ET0 and FAO Kc when all days available.
- History-based p10/median/p90 simulation, dry/wet rainfall scenario,
  temperature threshold **flags** if sourced threshold given, alert threshold.
- Pydantic integration models; regenerated example JSON; automated tests.

## Values still *not legitimately knowable* from crop-name references alone

- RUSLE field- and management-specific C-factors (erosion criterion)
- Retained dry biomass per crop with the farmer's residue management practice
  (organic matter input criterion)
- Dated APMC/farmgate price, expected marketable yield, cultivation and freight
  costs (market criterion)
- Total forage production, nutritive digestibility and feeding suitability by
  actual variety and handling
- Complete *five boundary* botanical phase days for the selected Devanahalli
  varieties, plus validated heat/moisture stress cutoffs
- The farm's own soil, irrigation, planting schedule and management
- Climate rasters/observations, per-crop seasonal ET0/ETc and year records from M2

**Do not enter zeros to remove nulls.** M3 should supply market/farmer values,
M2 provides climate/terrain/vegetation and geospatial data, and M1 applies
verified formulae to the inputs. Some scores will remain `null` until then.

See `rootwise_engine/data/research_sources.md` for traceable source URLs.
