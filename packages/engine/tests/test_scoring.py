from rootwise_engine.data_loader import load_crops
from rootwise_engine.models import Priorities, Climate
from rootwise_engine.scoring import score_crop

def test_missing_criterion_remains_null():
    crops=load_crops(); s=score_crop(crops[0],Priorities(),Climate(),crops)
    assert s.subscores['market_suitability'].value is None
    assert s.scored_weight_fraction < 1

def test_crop_eligibility_and_biology():
    crops=load_crops(); s=score_crop(crops[1],Priorities(),crops=crops)
    assert s.subscores['nitrogen_fixing'].value == 100
    assert s.total is not None

def test_adequacy_requires_all_inputs():
    crops=load_crops(); p=Priorities()
    a=score_crop(crops[0],p,Climate(seasonal_etc_mm=400,seasonal_effective_rainfall_mm=200),crops)
    assert a.subscores['water_use'].method=='relative_inverse_FAO_seasonal_ET_reference'
    b=score_crop(crops[0],p,Climate(seasonal_etc_mm=400,seasonal_effective_rainfall_mm=200,seasonal_irrigation_mm=0),crops)
    assert b.subscores['water_use'].method=='relative_inverse_FAO_seasonal_ET_reference'
    b2=score_crop(crops[0],p,Climate(data_kind='modelled',source_url='https://example.org/synthetic-test-only',seasonal_etc_by_crop_mm={'ragi':400},seasonal_effective_rainfall_mm=200,seasonal_irrigation_mm=0),crops)
    assert b2.subscores['water_use'].value == 50
