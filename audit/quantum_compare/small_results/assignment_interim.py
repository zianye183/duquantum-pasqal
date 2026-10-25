"""Explicitly scoped completed assignment-stage interim; global final gate unchanged."""
from pathlib import Path
import json,statistics,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from aggregate import inspect,canonical,METRICS
H=Path(__file__).resolve().parent

def main():
 audit,all_studies=inspect();c=audit['coverage']['assignment'];assert c['winners']==16 and c['case_arm_rows']==c['converged_rows']==320 and c['completed_fresh_trials']==512 and c['completion_marker']
 # Only unfinished ground-stage coverage is permitted. Any integrity error fails closed.
 allowed=('Missing completion marker full_encoding','Missing winner rule','Trial budget/duplicate trial rule','Pulse not frozen winner ')
 for error in audit['errors']:
  if error.startswith(allowed):
   if error.startswith('Pulse not frozen winner ') and '/full_ground_tuning/' not in error:raise ValueError(error)
   continue
  if error.startswith('Missing case arm ') and '/full_ground_tuning/' in error:continue
  raise ValueError(error)
 studies=[s for s in all_studies if s['family']=='assignment'];assert len(studies)==16;pairs=[];summaries=[]
 for s in studies:
  header={k:v for k,v in s.items() if k!='rows'};rs=[r for r in s['rows'] if r['split']=='evaluation'];assert len(rs)==10
  for seed in sorted({r['instance_seed'] for r in rs}):
   arms={r['evaluated_arm']:r for r in rs if r['instance_seed']==seed};assert set(arms)=={'intended','geometric'} and canonical(arms['intended']['pulse'])==canonical(arms['geometric']['pulse'])
   pairs.append(dict(**header,instance_seed=seed,split='evaluation',pulse=arms['intended']['pulse'],arms=arms,geometric_minus_intended={k:arms['geometric']['probabilities'][k]-arms['intended']['probabilities'][k] for k in METRICS}))
  for arm in ['intended','geometric']:
   selected=[r for r in rs if r['evaluated_arm']==arm]
   summaries.append(dict(**header,evaluated_arm=arm,metrics={k:dict(mean=statistics.mean(r['probabilities'][k] for r in selected),minimum=min(r['probabilities'][k] for r in selected),maximum=max(r['probabilities'][k] for r in selected)) for k in METRICS}))
 fair=[]
 for row in summaries:
  if row['method']!='tpe':continue
  rand=next(r for r in summaries if r['method']=='random' and all(r[k]==row[k] for k in ['formulation','trained_arm','evaluated_arm']))
  fair.append(dict(tpe_study=row['study'],random_study=rand['study'],evaluated_arm=row['evaluated_arm'],trials_each=32,random_reference_reused=True,independent_comparisons=False,difference_of_means={k:row['metrics'][k]['mean']-rand['metrics'][k]['mean'] for k in METRICS}))
 result=dict(status='completed_assignment_stage_interim_only',generated_at=datetime.now(ZoneInfo('America/New_York')).isoformat(),global_final_gate_ready=audit['ready'],assignment_coverage=c,ground_stage_coverage=audit['coverage']['full_encoding'],evaluation_instances=sorted({r['instance_seed'] for r in pairs}),summaries=summaries,paired_instances=pairs,fair_budget_comparisons=fair,source_hashes=audit['source_hashes'],report_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limitations=['Evaluation instances were already inspected in earlier work; retrospective rather than untouched test set.','Both formulations valid, but alternative formulation oracle-informed; not deployable penalty learning.','Development-only selection preserved; evaluation outcomes do not choose winners or trigger retuning.','Three TPE seeds retained individually; one random seed per formulation/trained arm reused across comparisons; no pooled-best TPE claim.','Empirical successive-step TV<0.001 supports only absolute stability; rare full-encoding probabilities below0.001 have no relative-precision guarantee.','No many-shot success predictions exported. No hardware validation or noise model.','Other objective/pulse-family study remains unfinished, so this is not the final goal report.'])
 (H/'ASSIGNMENT_INTERIM.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 lines=['# Completed assignment-objective tuning: interim evaluation','', 'The alternative formulation produces substantially higher assignment success in this diagnostic, but geometric interactions still reduce performance and leave severe instance-to-instance variation. Across the three searches trained on intended interactions, evaluation feasibility averages 84.1–95.6% for the alternative formulation versus 9.0–9.85% for the original formulation. Applying each identical alternative-formulation pulse to geometric interactions lowers mean feasibility to 27.2–35.6%; the worst instance is below 0.1% for every seed. This is formulation-dependent evidence, not a guarantee of generalization or deployable penalty selection.','', 'Adaptive optimization did not consistently beat the equally budgeted random search. For the alternative formulation, the single random-search run has higher evaluation mean assignment-optimum probability than each of the three adaptive runs on their respective training interaction models. This descriptive result does not prove random search generally superior; one random replication and 32 trials per run limit the conclusion.','', 'This is the completed assignment-objective stage only. The other objective/pulse-family search is unfinished, and the global final-report gate remains unchanged. All 512 declared trials, 16 winners and 320 case/arm rows are present; all saved rows pass their empirical refinement checks. Evaluation uses five saved instances, with every winner tested unchanged on both interaction models. No evaluation outcome selected a winner or triggered a new simulation.','', 'Each table entry is **mean [minimum] percentage across five instances**. **low** means the estimate is below the 0.1% reporting floor; it is not a certified upper bound and no relative precision is asserted. “Original optimum” accepts the correct clustering assignment even when its slack bits do not satisfy the full encoding; “full optimum” requires both. Training arm identifies the interaction model used for development optimization. All three adaptive-search seeds and the one equally budgeted random run are retained separately.']
 for form in ['original','alternative']:
  for trained in ['intended','geometric']:
   lines+=['',f'## {form.capitalize()} formulation; trained on {trained} interactions','', '| Search | Evaluated interactions | Feasible | Original optimum | Full optimum |','|---|---|---:|---:|---:|']
   for row in [r for r in summaries if r['formulation']==form and r['trained_arm']==trained]:
    pct=lambda p:'low' if p<.001 else f'{100*p:.3g}'
    cells=[f"{pct(row['metrics'][k]['mean'])} [{pct(row['metrics'][k]['minimum'])}]" for k in ['feasible','optimal','optimal_full_encoding']]
    lines.append('| '+f"{row['method']} {row['optimizer_seed']} | {row['evaluated_arm']} | "+' | '.join(cells)+' |')
 lines+=['','## Per-instance paired evidence','','The JSON contains all 80 winner/instance pairs, both sets of probabilities, their geometric-minus-intended differences, identical pulse parameters, numerical histories summarized by final step and adjacent-step discrepancy, source paths and hashes. It also contains all 24 separate equal-budget adaptive-minus-random comparisons. The same random result is reused, so these comparisons are not independent replications.','', '## Interpretation limits','']+['- '+x for x in result['limitations']]
 (H/'ASSIGNMENT_INTERIM.md').write_text('\n'.join(lines)+'\n');print(json.dumps(dict(coverage=c,pairs=len(pairs),summaries=len(summaries),fair_comparisons=len(fair),global_gate_ready=audit['ready'])))
if __name__=='__main__':main()
