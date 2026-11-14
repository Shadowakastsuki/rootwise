import yaml
from pathlib import Path
from rootwise_engine.api import recommend,simulate
from rootwise_engine.models import RecommendRequest, SimRequest
from rootwise_engine.data_loader import load_crops,load_variety_profiles,load_criteria,load_glossary

def test_eight_crop_references_have_accurate_provenance():
    crops=load_crops()
    assert len(crops)==8
    assert len({c.id for c in crops})==8
    assert all(c.scientific_name and c.kannada and c.source_urls for c in crops)
    assert all(c.phenology_days is None for c in crops)

def test_tn_varieties_are_separate_not_used_as_bengaluru_phases():
    d=load_variety_profiles()
    assert len(d['varieties'])==10
    assert not d['metadata']['five_phase_boundaries_verified']

def test_recommend_contract_has_all_six_keys_and_provenance():
    r=recommend(RecommendRequest())
    assert len(r.candidate_scores)==8
    assert len(r.strategies)==3
    assert all(len(c.subscores)==6 for c in r.candidate_scores)
    assert all(s.evidence.source_urls for s in r.strategies)
    assert r.evidence.needs_local_review

def test_simulation_without_M2_returns_no_fake_bands():
    result=simulate(SimRequest(recommendation=RecommendRequest()))
    assert len(result)==8
    assert all(x.band is None for x in result)

def test_criteria_and_glossary_exportable():
    assert 'market_suitability' in load_criteria()['criteria']
    assert 'NDVI' in load_glossary()
