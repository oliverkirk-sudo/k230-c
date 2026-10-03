#!/usr/bin/env python3
"""Static screening only. Dedicated reset-pad applicability and ramps remain gates."""
from pathlib import Path
import json,sys
b=Path(__file__).resolve().parents[1];t=.0015
lo=.6*.99*(1+200000*(1-t)/(100000*(1+t)))
hi=.6*1.01*(1+200000*(1+t)/(100000*(1-t)))
high_temp='--nexperia' in sys.argv
if high_temp:
 rail=next(r for r in json.load(open(b/'cad/high-temp-candidate/scaled-feedback-validation.json'))['rails'] if r['rail']=='1V8')
 lo=rail['static_min_with_bias_V'];hi=rail['static_max_with_bias_V']
leak=.3e-6+(.75e-6 if high_temp else .5e-6)
voh_loss=.11 if high_temp else .1
vol=.39 if high_temp else .35
vtp=1.31 if high_temp else 1.29
node_hi=lo-leak*100000*1.01
out_hi=lo-voh_loss
soc_hi=.65*lo;soc_lo=.35*lo
sink=hi/19000+10e-6
r={'scope':'CONDITIONAL_STATIC_VALID_SUPPLY_ONLY','supply_min_V':lo,'supply_max_V':hi,'intermediate_leakage_max_A':leak,'intermediate_high_min_V':node_hi,'intermediate_VTplus_max_at_1p65V':vtp,'intermediate_low_max_V':.4,'intermediate_VTminus_min_at_1p65V':.47,'final_high_min_V':out_hi,'conditional_soc_VIH_V':soc_hi,'high_margin_V':out_hi-soc_hi,'final_low_max_V':vol,'conditional_soc_VIL_V':soc_lo,'low_margin_V':soc_lo-vol,'low_sink_including_19k_PU_and_10uA_A':sink,'buffer_spec_test_sink_A':.0019,'limitations':['Static regulator tolerance only; distribution/ripple excluded.','Numerical general-I/O limits not explicitly guaranteed for dedicated RSTN.','Schmitt thresholds tabulated at discrete supply point; full-range interpretation needs qualification.','MR assertion150ns is typical, not a guaranteed maximum.','Below-valid-supply and arbitrary brownout reset are not qualified.']}
assert node_hi>vtp and .4<.47 and out_hi>soc_hi and vol<soc_lo and sink<.0019
(b/'cad/high-temp-candidate/buffered-reset-static-screen.json' if high_temp else b/'engineering/reset/buffered-reset-static-screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
