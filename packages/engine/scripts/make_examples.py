"""Generate real engine outputs, not hand-authored pretend observed data."""
import json
from pathlib import Path
import sys
# Allow regeneration from an extracted source tree before editable installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rootwise_engine.api import recommend, simulate
from rootwise_engine.models import RecommendRequest, SimRequest

HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'examples';OUT.mkdir(exist_ok=True)

def emit(name, obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,default=str)+'\n',encoding='utf-8')

req=RecommendRequest.model_validate({"field":{"region_id":"devanahalli","lat":13.25,"lon":77.71,"water_access":"unknown"},"priorities":{"water_use":80,"forage_value":60,"nitrogen_fixing":90,"erosion_reduction":70,"organic_matter":70,"market_suitability":50},"climate":{"data_kind":"missing"}})
response=recommend(req)
for name,obj in [("recommend_request.json",req.model_dump(mode='json')),("recommend_response.json",response.model_dump(mode='json'))]: emit(name,obj)
sim=SimRequest(recommendation=req,alert_threshold_score=50)
emit('simulate_request.json',sim.model_dump(mode='json'))
emit('simulate_response.json',[x.model_dump(mode='json') for x in simulate(sim)])
print('Created 4 example contract JSON files (unknowns remain null).')
