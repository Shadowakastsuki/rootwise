from datetime import date
from rootwise_engine.data_loader import load_crops
from rootwise_engine.phase import current_phase

def test_no_fabricated_phenology():
    c=load_crops()[0]
    assert current_phase(c,date(2025,7,1),date(2025,7,30))['phase']=='unknown'

def test_sowing_date_is_known():
    c=load_crops()[0]
    assert current_phase(c,date(2025,7,1),date(2025,7,1))['phase']=='sowing'

def test_documented_phase_boundaries():
    c=load_crops()[0].model_copy(deep=True)
    c.phenology_days={'sowing':0,'vegetative':8,'flowering':50,'grain_fill':70,'harvest':100}
    # These offsets are TEST fixtures only, never production reference data.
    assert current_phase(c,date(2025,1,1),date(2025,3,2))['phase']=='flowering'
