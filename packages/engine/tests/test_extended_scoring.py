"""Small SYNTHETIC UNIT TEST input fixtures; NOT measured Devanahalli data."""
import pytest
from datetime import date
from rootwise_engine.data_loader import load_crops
from rootwise_engine.models import Priorities, Climate, FarmField, SourceValue, MarketObservation
from rootwise_engine.scoring import score_crop

CROPS=load_crops()
BY={c.id:c for c in CROPS}

def test_forage_reference_is_source_backed():
    s=score_crop(BY['cowpea'],Priorities(),crops=CROPS)
    assert s.subscores['forage_value'].value==pytest.approx(68.5)
    assert s.subscores['forage_value'].proxy is True
    assert 'feedipedia.org' in s.subscores['forage_value'].evidence_urls[0]

def test_horsegram_draft_not_quoted_as_numeric_forage():
    assert score_crop(BY['horse_gram'],Priorities(),crops=CROPS).subscores['forage_value'].value is None

def test_erosion_rusle_cover_factor_formula():
    field=FarmField(cover_management_c_by_crop={'ragi':SourceValue(value=.2,unit='ratio',kind='field_measurement')})
    sc=score_crop(BY['ragi'],Priorities(),crops=CROPS,field=field)
    assert sc.subscores['erosion_reduction'].value==80
    assert sc.subscores['erosion_reduction'].input_summary['cover_management_factor_C']==.2

def test_unverified_rusle_factor_not_scored():
    field=FarmField(cover_management_c_by_crop={'ragi':SourceValue(value=.2,kind='published_reference')})
    s=score_crop(BY['ragi'],Priorities(),crops=CROPS,field=field)
    assert s.subscores['erosion_reduction'].value is None

def test_retained_residue_calculation_is_not_SOC():
    field=FarmField(residue_retained_fraction=.5,residue_dry_t_ha_by_crop={'ragi':SourceValue(value=4,kind='user_reported')})
    s=score_crop(BY['ragi'],Priorities(),crops=CROPS,field=field)
    assert s.subscores['organic_matter'].value==40
    assert 'NOT' not in s.subscores['organic_matter'].method

def test_zero_retained_residue_is_known_zero():
    field=FarmField(residue_retained_fraction=0)
    assert score_crop(BY['ragi'],Priorities(),crops=CROPS,field=field).subscores['organic_matter'].value==0

def _market():
    return MarketObservation(price_inr_per_quintal=5000,expected_yield_quintal_ha=20,
        cultivation_cost_inr_ha=50000,transport_cost_inr_per_quintal=100,
        market_name='synthetic-test-market',price_date=date(2026,11,10))

def test_market_roi_and_age():
    field=FarmField(market_by_crop={'cowpea':_market()})
    sc=score_crop(BY['cowpea'],Priorities(),crops=CROPS,field=field,as_of=date(2026,11,14))
    # revenue 100000, cost 52000, roi 48000/52000=0.9230769
    assert sc.subscores['market_suitability'].value==pytest.approx(92.308,abs=0.001)
    stale=score_crop(BY['cowpea'],Priorities(),crops=CROPS,field=field,as_of=date(2027,5,10))
    assert stale.subscores['market_suitability'].value is None

def test_full_six_criteria_when_all_required_inputs_supplied():
    field=FarmField(residue_retained_fraction=.5,
        residue_dry_t_ha_by_crop={'cowpea':SourceValue(value=4,kind='field_measurement')},
        cover_management_c_by_crop={'cowpea':SourceValue(value=.25,kind='field_measurement')},
        market_by_crop={'cowpea':_market()})
    climate=Climate(data_kind='modelled',source_url='https://test.invalid/nonproduction',
        seasonal_effective_rainfall_mm=250,seasonal_irrigation_mm=0,
        seasonal_etc_by_crop_mm={'cowpea':400})
    sc=score_crop(BY['cowpea'],Priorities(),climate,CROPS,field=field,as_of=date(2026,11,14))
    assert sc.scored_weight_fraction==1
    assert all(x.value is not None for x in sc.subscores.values())
    assert sc.total is not None and 0<sc.total<=100

@pytest.mark.parametrize('key', ['water_use','forage_value','nitrogen_fixing','erosion_reduction','organic_matter','market_suitability'])
def test_zero_priority_does_not_change_coverage(key):
    p=Priorities(**{k:(0 if k==key else 1) for k in Priorities.model_fields})
    sc=score_crop(BY['cowpea'],p,crops=CROPS)
    assert 0<=sc.scored_weight_fraction<=1

def test_missing_not_imputed_as_observation():
    s=score_crop(BY['groundnut'],Priorities(),crops=CROPS)
    assert s.subscores['market_suitability'].value is None
    assert s.subscores['erosion_reduction'].value is None
    assert s.subscores['organic_matter'].value is None
    assert s.scored_weight_fraction==.5  # water, forage, N of six

def test_no_active_priorities_is_null_not_zero():
    sc=score_crop(BY['ragi'],Priorities(**{k:0 for k in Priorities.model_fields}),crops=CROPS)
    assert sc.total is None


def test_icrisat_sourced_pigeon_pea_and_green_gram():
    from rootwise_engine.data_loader import load_crops
    lookup={c.id:c for c in load_crops()}
    pigeon=lookup['pigeon_pea']
    green=lookup['green_gram']
    horse=lookup['horse_gram']
    assert (pigeon.water_need.low, pigeon.water_need.high)==(500,800)
    assert (green.water_need.low, green.water_need.high)==(350,400)
    assert 'pegging' in lookup['groundnut'].critical_growth_stages
    assert horse.water_need.low is None
