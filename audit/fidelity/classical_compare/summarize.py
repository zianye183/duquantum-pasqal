"""Summaries preserve formulation/cohort and exact-vs-bounded distinctions."""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT=Path(__file__).resolve().parent
exact=json.loads((OUT/'small_results.json').read_text())
groups={}
for case in exact['rows']:
    for variant,r in case['variants'].items():
        if r is None:continue
        key=(case['tier'],case['cohort'],case['encoding'],case['embedder'],case['controls'],variant)
        groups.setdefault(key,[]).append((case,r))
rows=[]
for key,items in sorted(groups.items()):
    row=dict(zip(['tier','cohort','encoding','embedder','controls','variant'],key))
    row.update(conditions=len(items),instances=len(set(c['instance_seed'] for c,r in items)),
        all_minima_feasible=sum(r['feasible']['all_ground_states'] for c,r in items),
        any_minimum_feasible=sum(r['feasible']['any_ground_state'] for c,r in items),
        all_minima_original_optimal=sum(r['optimal']['all_ground_states'] for c,r in items),
        any_minimum_original_optimal=sum(r['optimal']['any_ground_state'] for c,r in items),
        unique_minimum=sum(r['ground_state_count']==1 for c,r in items),
        feasible_energy_gap_min=min(r['feasible']['lowest_energy_gap'] for c,r in items),
        feasible_energy_gap_max=max(r['feasible']['lowest_energy_gap'] for c,r in items))
    rows.append(row)
(OUT/'exact_summary.json').write_text(json.dumps(rows,indent=2)+'\n')
with (OUT/'exact_summary.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
variants=['intended','pairs_only','actual_endpoint']
labels=['Intended\nQUBO','Only pair\ndistortion','Actual\nendpoint']
colors=['#267e98','#d89a42','#9e698e']
for ax,(tier,encoding,title) in zip(axes,[('S','slack','Small textbook · 14 atoms'),('M','reduced','Medium reduced · 20 atoms')]):
    cases=[c for c in exact['rows'] if c['cohort']=='primary' and c['tier']==tier and c['encoding']==encoding]
    vals=[sum(c['variants'][v]['feasible']['any_ground_state'] for c in cases) for v in variants]
    ax.bar(range(3),vals,color=colors,width=.65)
    for i,v in enumerate(vals):ax.text(i,v+len(cases)*.025,f'{v}/{len(cases)}',ha='center',fontweight='bold',fontsize=13)
    ax.set_ylim(0,len(cases)*1.2);ax.set_xticks(range(3),labels);ax.set_ylabel('Layouts with any feasible minimum')
    ax.set_title(title+'\n'+str(len(set(c['instance_seed'] for c in cases)))+' independent problems',fontsize=13)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.suptitle('Classically solving the distorted energy gives infeasible answers',fontsize=15)
fig.supxlabel('Exact enumeration of every bitstring; all tied minima checked.\nCounts describe saved layouts, not independent problems or quantum success probabilities.',fontsize=10)
for ext in ['png','svg']:fig.savefig(OUT/('exact_comparison.'+ext),dpi=170)
plt.close(fig)
print(json.dumps({'exact_cases':exact['cases'],'summary_rows':len(rows),'figures_created':2}))
