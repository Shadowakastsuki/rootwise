from rootwise_engine.api import simulate
from rootwise_engine.models import SimRequest, RecommendRequest, HistoricalYear, Climate

def test_no_fabricated_historical_band():
    rows=simulate(SimRequest(recommendation=RecommendRequest()))
    assert len(rows)==8
    assert all(r.band is None and r.status=='insufficient_historical_data' for r in rows)

def test_real_formula_on_synthetic_test_fixture():
    # These are synthetic test fixtures, NOT NASA Devanahalli values.
    years=[HistoricalYear(year=2020+i,climate=Climate(data_kind='modelled',source_url='https://example.org/test-only',seasonal_etc_by_crop_mm={c:400 for c in ['ragi','groundnut','horse_gram','cowpea','pigeon_pea','green_gram','sorghum','foxtail_millet']},seasonal_effective_rainfall_mm=100+100*i,seasonal_irrigation_mm=0)) for i in range(4)]
    rows=simulate(SimRequest(recommendation=RecommendRequest(),historical_years=years,alert_threshold_score=50))
    assert all(x.band is not None and x.band.low_p10<=x.band.median_p50<=x.band.high_p90 for x in rows)
    assert rows[0].band.n_years==4

def test_temperature_delta_requires_unavailable_calibration():
    r=simulate(SimRequest(recommendation=RecommendRequest(),temperature_delta_c=2))[0]
    assert 'temperature slider does not change scores' in r.evidence.missing_information[-1]
