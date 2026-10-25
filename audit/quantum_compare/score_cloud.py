"""Score raw cloud counts against original constraints, retaining missing cases."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path

import numpy as np

from formulations import classify_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes, shots):
    z = 1.959963984540054
    p = successes / shots
    denominator = 1 + z*z/shots
    middle = (p + z*z/(2*shots))/denominator
    half = z*np.sqrt(p*(1-p)/shots + z*z/(4*shots*shots))/denominator
    return [max(0., float(middle-half)), min(1., float(middle+half))]


def score_counts(counts, atom_order, target):
    """Cloud bitstring position follows result atom_order, not lexical ID sort."""
    n = target['atoms']
    logical_order = [f'q{i}' for i in range(n)]
    if len(atom_order) != n or set(atom_order) != set(logical_order):
        raise ValueError('Result must contain every logical atom exactly once')
    if not counts or any(not isinstance(c, int) or isinstance(c, bool) or c < 0
                         for c in counts.values()):
        raise ValueError('Expected nonempty integer counts')
    if any(len(b) != n or set(b)-{'0', '1'} for b in counts):
        raise ValueError('Malformed raw bitstrings')
    weights = np.array(list(counts.values()), dtype=np.int64)
    shots = int(weights.sum())
    if shots <= 0:
        raise ValueError('No shots')
    columns = [atom_order.index(q) for q in logical_order]
    bits = np.array([[int(v) for v in b] for b in counts], dtype=np.int8)[:, columns]
    masks = classify_bits(bits, target, target['encoding'])
    out = {'shots': shots, 'unique_bitstrings': len(counts), 'metrics': {}}
    for name, mask in masks.items():
        if mask.dtype != bool:
            continue
        count = int(weights[mask].sum())
        out['metrics'][name] = {'count': count, 'rate': count/shots,
                               'shot_wilson_95': wilson(count, shots)}
    good = masks['feasible'] & (weights > 0)
    out['best_feasible_cost'] = float(masks['cost'][good].min()) if good.any() else None
    out['conditional_feasible_cost'] = (
        float(weights[good] @ masks['cost'][good] / weights[good].sum()) if good.any() else None)
    return out


def resolve_alias(prepared, result, entry, files, state):
    """Resolve one byte-identical reuse without manufacturing a new observation."""
    aliases_path = prepared/'ALIASES.json'
    binding = json.loads((prepared/'ALIAS_PROVENANCE.json').read_text())
    if (binding['aliases_sha256'] != digest(aliases_path) or
            binding['frozen_manifest_sha256'] != digest(prepared/'FROZEN_MANIFEST.json')):
        raise ValueError('Alias provenance binding differs')
    aliases = json.loads(aliases_path.read_text())['aliases']
    matches = [a for a in aliases if a['id'] == entry['id']]
    if len(matches) != 1 or state.get('independent_evidence') is not False:
        raise ValueError('Alias must have one declaration and no independent evidence')
    alias = matches[0]
    source = Path(alias['alias_of'])
    source_prepared = Path(alias['source_prepared_path'])
    source_manifest = Path(alias['source_manifest_path'])
    if (alias['source_manifest_sha256'] != digest(source_manifest) or
            alias['source_input_digest'] != entry['digest']):
        raise ValueError('Alias source provenance pin differs')
    if not all(p.is_absolute() for p in [source, source_prepared, source_manifest]):
        raise ValueError('Alias source paths must be absolute')
    if source.resolve() != Path(state['alias_of']).resolve() or source.resolve() == result.resolve():
        raise ValueError('Alias source mismatch or self-reference')
    if state.get('digest') != entry['digest']:
        raise ValueError('Alias destination digest mismatch')
    source_entries = json.loads(source_manifest.read_text())['jobs']
    matches = [e for e in source_entries if e['id'] == entry['id']]
    if len(matches) != 1 or matches[0]['digest'] != entry['digest']:
        raise ValueError('Alias source is not the same frozen job')
    if source_prepared.resolve() != (source_manifest.parent/entry['id']).resolve():
        raise ValueError('Alias prepared folder does not belong to source manifest')
    for destination in files:
        original = source_prepared/destination.name
        if original.read_bytes() != destination.read_bytes():
            raise ValueError('Alias input bytes differ')
        if digest(original) != alias[destination.stem+'_sha256']:
            raise ValueError('Alias declared input hash differs')
    source_state_path = source/'state.json'
    source_state = (json.loads(source_state_path.read_text()) if source_state_path.exists()
                    else {'status': 'not_observed'})
    if source_state.get('status') == 'alias':
        raise ValueError('Nested aliases are unsupported')
    if source_state_path.exists() and source_state.get('digest') != entry['digest']:
        raise ValueError('Alias source result digest differs')
    provenance = {'independent_evidence': False, 'alias_of': str(source),
                  'alias_state_sha256': digest(result/'state.json'),
                  'aliases_sha256': digest(aliases_path),
                  'source_prepared_manifest_sha256': digest(source_manifest)}
    return source, source_state_path, source_state, provenance


def analyze(prepared, results):
    manifest_path = prepared/'FROZEN_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    rows = []
    for entry in manifest['jobs']:
        folder, result = prepared/entry['id'], results/entry['id']
        files = [folder/(part+'.json') for part in ['sequence', 'config', 'metadata']]
        if hashlib.sha256(b''.join(p.read_bytes() for p in files)).hexdigest() != entry['digest']:
            raise ValueError('Prepared input changed')
        meta = json.loads(files[-1].read_text())
        state_path = result/'state.json'
        state = json.loads(state_path.read_text()) if state_path.exists() else {'status': 'not_observed'}
        provenance = {'independent_evidence': True}
        if state['status'] == 'alias':
            result, state_path, state, provenance = resolve_alias(
                prepared, result, entry, files, state)
        row = {'id': entry['id'], 'status': state['status'], 'pair_id': meta['pair_id'],
               'interaction_mode': meta['interaction_mode'], 'backend': meta['backend'],
               'target_id': meta.get('target', {}).get('id'), 'prepared_digest': entry['digest']}
        row.update(provenance)
        if state['status'] == 'completed':
            if state['digest'] != entry['digest']:
                raise ValueError('Result does not match frozen input')
            counts_path = result/'counts.json'
            row.update(score_counts(json.loads(counts_path.read_text()),
                                    state['result_atom_order'], meta['target']))
            if row['shots'] != meta['shots']:
                raise ValueError('Incomplete shot count')
            row['counts_sha256'] = digest(counts_path)
            row['state_sha256'] = digest(state_path)
            row['elapsed_submission_to_observation_seconds'] = (
                datetime.fromisoformat(state['finished_at']) -
                datetime.fromisoformat(state['submitted_at'])).total_seconds()
        rows.append(row)
    pairs = []
    for pair_id in sorted({r['pair_id'] for r in rows}):
        arms = {r['interaction_mode']: r for r in rows if r['pair_id'] == pair_id}
        complete = set(arms) == {'intended', 'geometric'} and all(r['status'] == 'completed' for r in arms.values())
        pair = {'pair_id': pair_id, 'complete': complete}
        if complete:
            pair['geometric_minus_intended'] = {
                k: arms['geometric']['metrics'][k]['rate']-arms['intended']['metrics'][k]['rate']
                for k in arms['intended']['metrics']}
        pairs.append(pair)
    return {'prepared_manifest_sha256': digest(manifest_path), 'rows': rows, 'pairs': pairs,
            'completed': sum(r['status'] == 'completed' for r in rows), 'total': len(rows),
            'reused_completed': sum(r['status'] == 'completed' and not r['independent_evidence'] for r in rows),
            'new_completed': sum(r['status'] == 'completed' and r['independent_evidence'] for r in rows),
            'reuse_scope': 'Reused rows are logical coverage, not additional independent observations or shots',
            'interval_scope': 'Shot sampling only; excludes problem variation and numerical approximation error',
            'elapsed_scope': 'Submission until local completion observation, including queue and polling latency',
            'cost': 'Unknown; not exposed by inspected SDK'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = analyze(args.prepared, args.results)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'completed': report['completed'], 'total': report['total']}))
