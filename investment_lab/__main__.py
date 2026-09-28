import argparse
from .runner import FUNCTIONS,run_all,run_project,summary

parser=argparse.ArgumentParser(description="Reproduce Fabio's frozen investment research")
parser.add_argument("project",choices=["all",*FUNCTIONS])
parser.add_argument("--output",default=None,help="Output directory (default: reports)")
args=parser.parse_args()
if args.project=="all":
    results=run_all(args.output)
    for pid,result in results.items():print(f"{pid}: {summary(pid,result)}")
else:
    result=run_project(args.project,args.output)
    print(summary(args.project,result))
