"""Read-only CSV bridge: import into a separate Excel sheet, never book trades."""
from pathlib import Path
import csv,json,sys
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"reports"/"excel";out.mkdir(exist_ok=True)
book=json.loads((ROOT/"data"/"current_book.json").read_text())
columns=["ticker","name","asset","currency","units","price","fx","asof","value","weight"]
rows=[{k:h[k] for k in columns} for h in book["holdings"]]
rows.append({"ticker":"CASH","name":"EUR cash","asset":"Cash","currency":"EUR","units":book["cash"],"price":1,"fx":1,"asof":book["asof"],"value":book["cash"],"weight":book["cash"]/book["nav"]})
with (out/"current_holdings.csv").open("w",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
for name in ["attribution_price_fx.csv","risk_risk_contributions.csv","rebalancing_rule_results.csv"]:
    (out/name).write_bytes((ROOT/"reports"/name).read_bytes())
print("Exported four CSV snapshots for Excel; no ledger or public book changed.")
