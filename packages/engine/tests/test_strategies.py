from rootwise_engine.api import recommend
from rootwise_engine.models import RecommendRequest

def test_three_unique_ranked_options_and_evidence():
    r=recommend(RecommendRequest())
    assert len(r.strategies)==3
    assert [s.rank for s in r.strategies]==[1,2,3]
    assert len({s.primary_crop_id for s in r.strategies})==3
    assert all(s.evidence.missing_information for s in r.strategies)
    assert len(r.candidate_scores)==8


def test_high_priority_slider_values():
    request=RecommendRequest.model_validate({"priorities":{"water_use":80,"nitrogen_fixing":90,"forage_value":60,"erosion_reduction":70,"organic_matter":70,"market_suitability":50}})
    assert len(recommend(request).strategies)==3
