# M1 <-> M2/M3/M4/M5 Contract and Testing Notes

## M3 setup

`pip install -e packages/engine`

```python
from rootwise_engine.api import recommend, simulate, field_status
from rootwise_engine.data_loader import load_crops, load_criteria, load_glossary

# M3 should validate request bodies with RecommendRequest or SimRequest.
```

The `examples/` directory has 4 real function-produced JSON contracts. If
these models change, rerun `python scripts/make_examples.py` and send the new
contracts to M3 and M4.

## Example M3 can pass WITHOUT pretending these are NASA observations

The following is a **field-input schema illustration**, not a real farm or
APMC quote. Input data are intentionally missing rather than fabricated.

```json
{
  "field": {
    "region_id": "devanahalli",
    "lat": 13.25,
    "lon": 77.71,
    "water_access": "unknown",
    "residue_retained_fraction": null,
    "cover_management_c_by_crop": {},
    "residue_dry_t_ha_by_crop": {},
    "market_by_crop": {},
    "phenology_override_days": null
  },
  "climate": {
    "data_kind": "missing",
    "source_url": null,
    "seasonal_effective_rainfall_mm": null,
    "seasonal_irrigation_mm": null,
    "seasonal_etc_by_crop_mm": {},
    "daily": [],
    "coverage": null
  }
}
```

A crop-specific optional market record (after M3 obtains genuine source data):

```json
"market_by_crop": {
  "cowpea": {
    "price_inr_per_quintal": null,
    "expected_yield_quintal_ha": null,
    "cultivation_cost_inr_ha": null,
    "transport_cost_inr_per_quintal": null,
    "market_name": null,
    "price_date": null,
    "price_source_url": null,
    "yield_source_url": null,
    "cost_source_url": null,
    "data_kind": "user_reported"
  }
}
```

In actual API submissions, omit that example until complete numeric values
and a valid `YYYY-MM-DD` date are present; the Pydantic `MarketObservation`
model correctly rejects a `null` numeric price.

## Per-feature responsibilities

- **M1:** source-labelled crop reference knowledge, scoring/normalization,
  three ranked screening strategies, phase/status, stress flags, scenario
  percentiles, contracts, unit tests and evidence.
- **M2:** versioned NASA/SMAP/HLS/GPM/POWER climate, moisture and bare-soil
  observations; grid alignment, data quality, exposure, season dates, slope and
  calibrated field-level erosion layer C factors if possible.
- **M3:** field and farmer inputs; location -> climate lookup; crop-specific
  prices and costs if collected; PostGIS tables; validation and endpoints.
- **M4:** crop bar chart, radar (nullable criterion values), band plot, phase
  with `unknown` state, confidence/evidence drawer, priorities.
- **M5:** map, evidence vocabulary and contextual stress warnings.

## Interpretation / validation

- `subscores[key].value = null` means **not known**, not zero or unfavorable.
- `total` is a conservative weighted **known-contribution index**, NOT a
  crop suitability probability. A crop with less source coverage can appear
  worse than a crop with more source coverage; M4 should show coverage.
- `confidence = low/medium` means documentation/data completeness, NOT
  statistical interval coverage of yield. No `high` until expert validation.
- `SimResult.band` contains p10/p50/p90 of **historical screening scores**,
  not yields and not predictive uncertainty intervals.
- `temperature_delta_c` adjusts optional threshold exceedance *counts* if
  crop threshold + sourced daily Tmax are supplied. The score is unchanged
  without validated heat-to-yield or heat-to-utility response parameters.
- Crop water ETc and rain must refer to the same actual sowing/harvest window.
- Bare field needs explicit direct observation; NDVI alone is insufficient.

## Quick local verification

```powershell
cd D:\Codes\rootwise\packages\engine
python -m pip install -e ".[dev]"
python -m pytest -q
python scripts/make_examples.py
python -c "from rootwise_engine.api import recommend; from rootwise_engine.models import RecommendRequest; r=recommend(RecommendRequest()); print([(s.primary_crop_id, s.score.total, s.score.scored_weight_fraction) for s in r.strategies])"
```

The automated tests use **synthetic test fixtures** with clearly
not-real inputs to verify formula arithmetic. They are NOT stored as actual
Devanahalli environmental data or market prices.
