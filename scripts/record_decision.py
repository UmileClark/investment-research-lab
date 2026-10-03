"""Append a forecast/resolution from a JSON file; commit publicly before the event."""
from pathlib import Path
import sys,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from investment_lab.decisionlog import append

if len(sys.argv)!=2: raise SystemExit('Usage: python scripts/record_decision.py input_record.json')
path=ROOT/'config/decision_register.json'; records=json.loads(path.read_text())
row=json.loads(Path(sys.argv[1]).read_text())
# Authorship time is stamped now, rather than accepting backdated user input.
row['created_at']=datetime.now(timezone.utc).isoformat()
updated=append(records,row)
path.write_text(json.dumps(updated,indent=2,ensure_ascii=False)+'\n')
print('Appended',row['id'],'— review and commit this register before the event. No trade created.')
