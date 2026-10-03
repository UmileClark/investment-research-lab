"""Prospective binary forecasts with an append-only hash chain and proper scores."""
from datetime import datetime
import hashlib
import json
import numpy as np
from .data import ROOT
from .analytics import result


def digest(record):
    body={k:v for k,v in record.items() if k!='hash'}
    return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def timestamp(s):
    t=datetime.fromisoformat(s.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('Timezone required')
    return t


def validate(records):
    previous='0'*64; seen=set(); forecasts={}; resolved=set(); last=None
    for row in records:
        if row['id'] in seen: raise ValueError('Duplicate record id')
        seen.add(row['id']); created=timestamp(row['created_at'])
        if last and created<last: raise ValueError('Out-of-order record')
        if row['previous_hash']!=previous or row['hash']!=digest(row): raise ValueError('Broken hash chain')
        if row['kind']=='forecast':
            p=row['probability']
            if isinstance(p,bool) or not isinstance(p,(float,int)) or not 0<=p<=1: raise ValueError('Probability must be in [0,1]')
            if timestamp(row['deadline'])<=created: raise ValueError('Forecast must precede deadline')
            if timestamp(row['information_cutoff'])>created: raise ValueError('Future evidence')
            for k in ['event','resolution_rule','source_url','alternative','invalidation']:
                if not isinstance(row[k],str) or not row[k].strip(): raise ValueError('Missing decision field: '+k)
            forecasts[row['id']]=row
        elif row['kind']=='resolution':
            f=forecasts.get(row['forecast_id'])
            if not f or row['forecast_id'] in resolved: raise ValueError('Unknown or resolved forecast')
            if created<timestamp(f['deadline']): raise ValueError('Resolution before deadline')
            if type(row['outcome']) is not int or row['outcome'] not in [0,1]: raise ValueError('Binary outcome required')
            if not row.get('evidence_url'): raise ValueError('Resolution evidence required')
            resolved.add(row['forecast_id'])
        else: raise ValueError('Unknown record kind')
        previous=row['hash'];last=created
    return forecasts


def append(records, row):
    candidate={**row,'previous_hash':records[-1]['hash'] if records else '0'*64}
    candidate['hash']=digest(candidate)
    validate([*records,candidate])
    return [*records,candidate]


def run():
    records=json.loads((ROOT/'config/decision_register.json').read_text());forecasts=validate(records)
    scored=[{'id':r['forecast_id'],'probability':forecasts[r['forecast_id']]['probability'],'outcome':r['outcome'],
             'brier':(forecasts[r['forecast_id']]['probability']-r['outcome'])**2} for r in records if r['kind']=='resolution']
    demo=[{'declared_probability':float(p),'expected_brier_if_true_probability_60pct':float(.6*(1-p)**2+.4*p*p)} for p in np.linspace(0,1,21)]
    summary=f"{len(forecasts)} prospective forecasts and {len(scored)} resolved outcomes are registered. "
    summary+=f"Mean binary Brier score: {np.mean([r['brier'] for r in scored]):.3f}." if scored else 'No forecasting skill score is claimed. The probability-scoring chart is a labelled mathematical demonstration.'
    return result(summary,{'register_status':[{'forecasts':len(forecasts),'resolved':len(scored),'chain_valid':True}],
                          'resolved_forecasts':scored,'synthetic_scoring_example':demo},
        {'kind':'lines','x':[r['declared_probability'] for r in demo],'series':[{'label':'Expected Brier loss · assumed true probability 60%','values':[r['expected_brier_if_true_probability_60pct'] for r in demo]}],
         'xlabel':'Declared probability','ylabel':'Expected squared probability error','title':'Synthetic proper-scoring demonstration · not personal forecasting results'},
        ['Register starts empty on 3 October 2026. Do not backfill historical probabilities.',
         'Forecasts require a dated cutoff, explicit binary outcome, source, alternative, invalidation condition and deadline; resolutions append a separate evidence-backed record.',
         'Binary Brier score = (probability − outcome)². Lower is better; compare to a preregistered base-rate benchmark before making skill claims.'],
        'A hash chain detects internal tampering, but the entire chain can be rewritten. External Git commit timestamps and public pre-event publication are necessary anchors, not independent audits. Honest entry dates and resolution evidence still require human review. Small or selectively resolved samples cannot establish calibration or investment skill. This register does not record trades or place orders.')
