"""Print transparent M1 crop screening and missing criteria from the current source DB.

This uses NO NASA/weather inputs unless you explicitly change the request model.
The scores are therefore NOT location-specific planting recommendations.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rootwise_engine.api import recommend
from rootwise_engine.models import RecommendRequest, CRITERIA

r = recommend(RecommendRequest())
print('ROOTWISE M1 v0.2 — Published references only, NOT planting advice')
print(f'{"Crop":18} {"Index":>7} {"Coverage":>10}  Missing criteria')
print('-' * 92)
for crop in r.candidate_scores:
    total = f'{crop.total:.2f}' if crop.total is not None else 'null'
    missing = ', '.join(key for key in CRITERIA if crop.subscores[key].value is None)
    print(f'{crop.crop_id:18} {total:>7} {crop.scored_weight_fraction:>9.0%}  {missing or "none"}')
print('\nTop three SCREENING choices (not a farming prescription):')
for s in r.strategies:
    print(f'{s.rank}. {s.name}: {s.primary_crop_id} ({s.score.total}) — {s.evidence.confidence} confidence')
print('\nSee rootwise_engine/data/research_sources.md for original sources and limitations.')
