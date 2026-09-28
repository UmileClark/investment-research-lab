"""Build and actually execute the project's simple, standard-Python notebooks.

Not a general Jupyter kernel runner: these notebooks use no magics or display
hooks. Each code cell is executed in order; exceptions abort the build.
"""
from pathlib import Path
import sys,json,io,contextlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from investment_lab.catalog import PROJECTS


for p in PROJECTS:
    pid=p["id"]
    cells=[
      {"cell_type":"markdown","metadata":{},"source":f"# {p['title']}\n\n{p['question']}\n\nAuthored 28 September 2026. Retrospective study; AI-assisted implementation.\n\n{p['method']}"},
      {"cell_type":"code","metadata":{},"source":"from pathlib import Path\nimport sys\nroot = Path.cwd()\nif not (root / 'investment_lab').exists():\n    root = root.parent\nif not (root / 'investment_lab').exists():\n    raise RuntimeError('Open this notebook from the project root or notebooks folder')\nsys.path.insert(0, str(root))\nfrom investment_lab.runner import run_project, summary\n","outputs":[],"execution_count":None},
      {"cell_type":"code","metadata":{},"source":f"result = run_project('{pid}')\nprint(summary('{pid}', result))\nprint('\\nLimitation:', result['limitation'])","outputs":[],"execution_count":None},
      {"cell_type":"markdown","metadata":{},"source":f"![Computed chart](../reports/{pid}.png)\n\n## Investment implication\n\n{p['decision']}\n\n## What could invalidate this interpretation?\n\n{p['falsifier']}\n\n## Investigate next\n\n{p['next']}\n\nFull numeric outputs and CSVs: `reports/{pid}.json` and `reports/{pid}_*.csv`. References: `reports/{pid}.md`."}
    ]
    namespace={"__name__":"__main__"};count=0
    for cell in cells:
        if cell["cell_type"]!="code":continue
        count+=1;capture=io.StringIO()
        with contextlib.redirect_stdout(capture):exec(compile(cell["source"],f"{pid}-cell-{count}","exec"),namespace)
        cell["execution_count"]=count
        cell["outputs"]=[{"output_type":"stream","name":"stdout","text":capture.getvalue()}] if capture.getvalue() else []
    notebook={"nbformat":4,"nbformat_minor":5,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":sys.version.split()[0]},"execution_note":"Code cells executed sequentially by scripts/execute_notebooks.py; no Jupyter magics used."},"cells":cells}
    for i,cell in enumerate(cells):cell["id"]=f"{pid}-{i}"
    (ROOT/"notebooks"/f"{pid}.ipynb").write_text(json.dumps(notebook,indent=2,ensure_ascii=False))
    print(pid,"executed",count,"code cells")
