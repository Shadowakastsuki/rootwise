"""Rootwise M1 offline/local smoke test using actual NASA POWER historical rainfall.

Place in packages/engine/scripts/test_devanahalli.py, run from packages/engine:
  python -m pip install requests pandas
  python scripts/test_devanahalli.py

This script downloads real NASA POWER data (or reads a previously downloaded CSV),
uses FAO's simplified monthly effective-rainfall method, and uses FAO published
crop-season water-need midpoints as *reference ETc proxies*. It assumes a
rainfed field with 0 mm irrigation solely for a TEST scenario.
NOT a validated crop suitability or irrigation recommendation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import requests

from rootwise_engine.api import recommend, simulate
from rootwise_engine.data_loader import load_crops
from rootwise_engine.models import Climate, HistoricalYear, RecommendRequest, SimRequest

LAT, LON = 13.25, 77.71  # Approximate Devanahalli town point; NOT surveyed farm
START, END = "20150101", "20251231"
PARAMS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN"]
API = "https://power.larc.nasa.gov/api/temporal/daily/point"
FAO_EFFECTIVE_RAIN = "https://www.fao.org/4/s2022e/s2022e08.htm"
FAO_CROP_WATER = "https://www.fao.org/4/s2022e/s2022e02.htm"
OUT = Path(__file__).resolve().parents[1] / "local_data" / "devanahalli"


def request_url() -> str:
    # The URL is used for provenance even when reading a cached CSV.
    req = requests.Request("GET", API, params={
        "parameters": ",".join(PARAMS), "community": "AG",
        "longitude": LON, "latitude": LAT,
        "start": START, "end": END, "format": "JSON", "time-standard": "LST",
    }).prepare()
    return req.url


def get_weather(csv_file: Path | None, refresh: bool) -> tuple[pd.DataFrame, str]:
    OUT.mkdir(parents=True, exist_ok=True)
    cached = OUT / "power_daily_2015_2025.csv"
    if csv_file:
        if not csv_file.is_file():
            raise FileNotFoundError(f"CSV file does not exist: {csv_file}")
        print(f"Reading NASA POWER CSV from {csv_file}")
        df = pd.read_csv(csv_file)
        # The earlier download_power.py produces a 'date' column.
        # NASA's direct CSV uses YEAR, MO, DY and a comment preamble.
        if "date" not in df.columns:
            raise ValueError("CSV must have a 'date' column. Use the generated download_power.py output, or run this script without --csv to download directly.")
        df["date"] = pd.to_datetime(df["date"], errors="raise")
        df = df.set_index("date")
        source = request_url()
    elif cached.is_file() and not refresh:
        print(f"Using cached NASA POWER data: {cached}")
        df = pd.read_csv(cached, parse_dates=["date"]).set_index("date")
        source = (OUT / "source_url.txt").read_text(encoding="utf-8").strip() if (OUT / "source_url.txt").exists() else request_url()
    else:
        print("Downloading real NASA POWER daily observations for 2015-2025 ...")
        response = requests.get(request_url(), timeout=180)
        response.raise_for_status()
        payload = response.json()
        if "properties" not in payload or "parameter" not in payload["properties"]:
            raise ValueError(f"Unexpected NASA response: {str(payload)[:500]}")
        df = pd.DataFrame(payload["properties"]["parameter"])
        df.index = pd.to_datetime(df.index, format="%Y%m%d", errors="raise")
        df.index.name = "date"
        source = response.url
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Invalid date index")
    df = df.sort_index()
    if df.index.has_duplicates:
        raise ValueError("Duplicate NASA POWER dates; cannot compute safe totals")
    for p in ("PRECTOTCORR", "T2M_MAX"):
        if p not in df.columns:
            raise ValueError(f"NASA POWER column missing: {p}")
    for p in PARAMS:
        if p in df:
            df[p] = pd.to_numeric(df[p], errors="coerce").replace([-999, -999.0, -9999], float("nan"))
    if (df["PRECTOTCORR"].dropna() < 0).any():
        raise ValueError("Negative precipitation found; review source quality")
    df.to_csv(cached, index_label="date")
    (OUT / "source_url.txt").write_text(source + "\n", encoding="utf-8")
    return df, source


def fao_effective_rain_monthly(p_mm: float) -> float:
    """FAO Crop Water Needs Chapter 4: simple effective-rainfall approximation.

    Only documented for terrain slopes at most about 4-5%. Local slope is
    UNKNOWN in this demo; results are exploratory, not site-calibrated.
    """
    if p_mm < 0:
        raise ValueError("Rainfall must be nonnegative")
    return max(0.0, 0.6 * p_mm - 10 if p_mm < 75 else 0.8 * p_mm - 25)


def reference_etc_proxies() -> dict[str, float]:
    """FAO crop-category seasonal water-need midpoints, NOT site ETc from ET0."""
    result = {}
    for crop in load_crops():
        if crop.water_need.low is not None and crop.water_need.high is not None:
            result[crop.id] = round((crop.water_need.low + crop.water_need.high) / 2, 3)
    return result


def yearly_climate(df: pd.DataFrame, year: int, source: str) -> tuple[Climate, dict] | None:
    # Fixed June-Sep test window; not a verified sowing calendar for all crops.
    season = df.loc[f"{year}-06-01":f"{year}-09-30"].copy()
    expected = len(pd.date_range(f"{year}-06-01", f"{year}-09-30"))
    if len(season) != expected or season["PRECTOTCORR"].isna().any():
        print(f"SKIPPING {year}: incomplete June-Sep precipitation data")
        return None
    full = df.loc[f"{year}-01-01":f"{year}-12-31"]
    expected_full = len(pd.date_range(f"{year}-01-01", f"{year}-12-31"))
    annual = float(full["PRECTOTCORR"].sum()) if len(full) == expected_full and full["PRECTOTCORR"].notna().all() else None
    monthly = season["PRECTOTCORR"].resample("MS").sum()
    gross = float(monthly.sum())
    peff = float(sum(fao_effective_rain_monthly(float(p)) for p in monthly))
    # Modelled fields are derived from observed NASA estimates + FAO formula,
    # not direct NASA observations. Irrigation=0 is a TEST ASSUMPTION.
    climate = Climate(
        source_id="NASA_POWER_rainfall_FAO_effective_rain_FAO_water_reference_demo",
        source_url=source,
        data_kind="modelled",
        annual_rainfall_mm=annual,
        seasonal_effective_rainfall_mm=round(peff, 3),
        seasonal_irrigation_mm=0.0,
        seasonal_etc_by_crop_mm=reference_etc_proxies(),
        coverage=1.0,
        notes=[
            "Rainfall from NASA POWER gridded daily estimates; NOT a farm rain gauge",
            "FAO monthly Peff approximation applied to fixed June-Sep window; local slope unknown",
            "FAO published seasonal crop water-need midpoints used as ETc PROXIES, not locally modelled ETc",
            "0 mm irrigation is a RAINFED TEST ASSUMPTION, not measured farm data",
            "No soil moisture or crop-specific growing calendars; score is screening only",
            f"FAO effective rainfall: {FAO_EFFECTIVE_RAIN}",
            f"FAO crop water references: {FAO_CROP_WATER}",
        ],
    )
    return climate, {
        "year": year, "season": "June-September (testing convention)",
        "seasonal_rainfall_mm": round(gross, 3),
        "modelled_effective_rainfall_mm": round(peff, 3),
        "annual_rainfall_mm": round(annual, 3) if annual is not None else None,
        "mean_season_tmax_c": round(float(season["T2M_MAX"].mean()), 3) if season["T2M_MAX"].notna().any() else None,
        "source_url": source,
        "status": "NASA gridded rainfall + FAO modelled effective rainfall + test irrigation assumption",
    }


def dump_json(name: str, value) -> None:
    path = OUT / name
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print("Saved:", path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=None, help="Use the CSV from download_power.py (must include a date column)")
    parser.add_argument("--refresh", action="store_true", help="Download again rather than using cached daily observations")
    args = parser.parse_args()
    df, source = get_weather(args.csv, args.refresh)
    climates = []
    summaries = []
    for year in range(2015, 2026):
        item = yearly_climate(df, year, source)
        if item is not None:
            climate, summary = item
            climates.append(HistoricalYear(year=year, climate=climate))
            summaries.append(summary)
    if len(climates) < 3:
        raise RuntimeError("Need at least 3 complete June-Sep historical seasons for the simulation")
    pd.DataFrame(summaries).to_csv(OUT / "historical_weather_summary.csv", index=False)
    print("\nActual NASA rainfall with FAO-derived testing estimates:")
    print(pd.DataFrame(summaries)[["year", "seasonal_rainfall_mm", "modelled_effective_rainfall_mm", "mean_season_tmax_c"]].to_string(index=False))
    # Use latest available year, not a made-up current weather snapshot.
    latest = climates[-1]
    req = RecommendRequest.model_validate({
        "field": {"region_id": "devanahalli", "lat": LAT, "lon": LON, "water_access": "rainfed"},
        "climate": latest.climate.model_dump(mode="json"),
    })
    rec = recommend(req)
    dump_json("recommend_request_real_weather_modelled_water.json", req.model_dump(mode="json"))
    dump_json("recommend_response_real_weather_modelled_water.json", rec.model_dump(mode="json"))
    print(f"\nRecommendation screening using {latest.year} climate (not a planting recommendation):")
    for s in rec.strategies:
        print(f"  {s.rank}. {s.primary_crop_id:16s} score={s.score.total} coverage={s.score.scored_weight_fraction:.2f} confidence={s.evidence.confidence}")
    for name, multiplier in [("baseline", 1.0), ("dry_30pct", 0.7), ("wet_30pct", 1.3)]:
        sim_req = SimRequest(recommendation=req, historical_years=climates, rain_multiplier=multiplier, alert_threshold_score=50.0)
        result = simulate(sim_req)
        dump_json(f"simulate_{name}_request.json", sim_req.model_dump(mode="json"))
        dump_json(f"simulate_{name}_response.json", [r.model_dump(mode="json") for r in result])
        print(f"\nWhat-if {name} (rain multiplier {multiplier}):")
        for item in result:
            if item.band:
                print(f"  {item.crop_id:16s} p10={item.band.low_p10:6.2f} median={item.band.median_p50:6.2f} p90={item.band.high_p90:6.2f} n={item.band.n_years}")
            else:
                print(f"  {item.crop_id:16s} unavailable (missing FAO water reference or complete input)")
    print("\nIMPORTANT: Rainfall observations are NASA-sourced; effective rainfall is FAO-modelled;")
    print("ETc is an FAO published seasonal reference proxy; irrigation=0 is a test assumption.")
    print("The temperature slider currently does NOT change M1 numerical scores.")
    print("FAO effective-rain method assumes gentle terrain (~4-5% slope maximum); field slope unverified.")
    print("Do not present these scores as validated local crop recommendations.")


if __name__ == "__main__":
    main()
