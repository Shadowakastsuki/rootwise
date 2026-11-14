from datetime import date, timedelta
from rootwise_engine.water import seasonal_etc_from_daily_et0
from rootwise_engine.models import Climate, DailyClimate
from rootwise_engine.data_loader import load_crops

def test_fao_simplified_etc_equals_sum_kc_times_et0():
    # Synthetic TEST ONLY: constant 4 mm/day ET0 is NOT Devanahalli historical data.
    crop=next(c for c in load_crops() if c.id=='groundnut')
    start=date(2024,7,1)
    ndays=sum(crop.fao_stage_lengths)
    climate=Climate(daily=[DailyClimate(date=start+timedelta(days=i),et0_mm=4) for i in range(ndays)])
    result=seasonal_etc_from_daily_et0(crop,start,climate)
    expected=sum(n*crop.kc[s]*4 for s,n in zip(('initial','development','mid','late'),crop.fao_stage_lengths))
    assert result['etc_mm']==round(expected,3)

def test_etc_does_not_interpolate_missing_days():
    c=next(c for c in load_crops() if c.id=='ragi')
    assert seasonal_etc_from_daily_et0(c,date(2025,1,1),Climate())['etc_mm'] is None

def test_horsegram_stage_lengths_not_invented():
    c=next(c for c in load_crops() if c.id=='horse_gram')
    assert seasonal_etc_from_daily_et0(c,date(2025,1,1),Climate())['etc_mm'] is None
