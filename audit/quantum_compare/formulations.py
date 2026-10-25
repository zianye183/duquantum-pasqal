"""Independent scoring and correctness-preserving textbook parameter rules.

Logical variable zero is least-significant by default. This is deliberately
explicit: Pulser/QuTiP basis conventions require conversion by the caller.
"""
from pathlib import Path
import itertools
import json
import numpy as np

TOL = 1e-8


def slack_weights(capacity):
    width = int(capacity).bit_length()
    return np.array([1 << b for b in range(width - 1)] +
                    [capacity - ((1 << (width - 1)) - 1)], dtype=int)


def classify_bits(bits, instance, encoding):
    """Classify logical-order binary rows without repair; all shots count."""
    z = np.asarray(bits)
    n, k, cap = instance['N'], instance['K'], instance['Q']
    q, c = np.asarray(instance['q']), np.asarray(instance['c'])
    weights = slack_weights(cap)
    expected = n * (k - 1) if encoding == 'reduced' else n*k + k*len(weights)
    if encoding not in ('slack', 'reduced') or z.ndim != 2 or z.shape[1] != expected:
        raise ValueError('Encoding and logical variable count must agree')
    if not np.isin(z, [0, 1]).all():
        raise ValueError('Only binary logical values are allowed')
    z = z.astype(np.int64)
    if encoding == 'slack':
        x = z[:, :n*k].reshape(-1, k, n).transpose(0, 2, 1)
        valid = (x.sum(axis=2) == 1).all(axis=1)
        helper = z[:, n*k:].reshape(-1, k, len(weights)) @ weights
    else:
        partial = z.reshape(-1, n, k-1)
        valid = (partial.sum(axis=2) <= 1).all(axis=1)
        x = np.concatenate([(1-partial.sum(axis=2))[:, :, None], partial], axis=2)
        helper = None
    loads = np.einsum('i,bik->bk', q, x)
    feasible = valid & (loads >= 0).all(axis=1) & (loads <= cap).all(axis=1)
    cost = np.zeros(len(z))
    for i, j in itertools.combinations(range(n), 2):
        cost += c[i, j] * (x[:, i, :] * x[:, j, :]).sum(axis=1)
    optimal = feasible & np.isclose(cost, instance['f_star'], atol=TOL, rtol=0)
    full = feasible if helper is None else feasible & (loads + helper == cap).all(axis=1)
    return {'assignment_valid': valid, 'feasible': feasible, 'optimal': optimal,
            'full_encoding_feasible': full, 'optimal_full_encoding': full & optimal,
            'cost': cost}


def basis_masks(instance, encoding, bit_order='little', zero_is_excited=False):
    """Return full state-vector masks, limited to <=20 variables.

    little means basis integer bit i maps to logical variable i; big reverses it.
    zero_is_excited=True complements every basis bit (e.g. |r>,|g> ordering).
    """
    n = instance['N']*(instance['K']-1) if encoding == 'reduced' else instance['K']*(instance['N']+len(slack_weights(instance['Q'])))
    if n > 20 or bit_order not in ('little', 'big'):
        raise ValueError('Use sample scoring above 20 variables; state order must be explicit')
    shifts = np.arange(n) if bit_order == 'little' else np.arange(n-1, -1, -1)
    z = ((np.arange(1 << n, dtype=np.uint64)[:, None] >> shifts.astype(np.uint64)) & 1).astype(np.int8)
    if zero_is_excited:
        z = 1-z
    return classify_bits(z, instance, encoding)


def score_probabilities(probabilities, masks):
    p = np.asarray(probabilities, dtype=float)
    if p.ndim != 1 or not np.isfinite(p).all() or (p < -1e-14).any():
        raise ValueError('Probabilities must be a finite nonnegative vector')
    if abs(p.sum()-1) > 1e-6:
        raise ValueError('Probability mass is not normalized; do not hide integrator errors')
    if any(len(v) != len(p) for v in masks.values()):
        raise ValueError('Probability and mask sizes differ')
    out = {name: float(p[v].sum()) for name, v in masks.items() if v.dtype == bool}
    mass = out['feasible']
    out['conditional_feasible_cost'] = float(p[masks['feasible']] @ masks['cost'][masks['feasible']] / mass) if mass > 0 else None
    out['normalization_error'] = float(p.sum()-1)
    return out


def first_feasible_assignment(instance):
    """Capacity-only lexicographic search, deliberately ignores objective/ref."""
    q, k, cap = instance['q'], instance['K'], instance['Q']
    loads = [0]*k
    result = [0]*len(q)
    def visit(i):
        if i == len(q):
            return tuple(result)
        seen = set()
        for v in range(k):
            if loads[v] in seen or loads[v]+q[i] > cap:
                continue
            seen.add(loads[v]); loads[v] += q[i]; result[i] = v
            answer = visit(i+1)
            loads[v] -= q[i]
            if answer is not None:
                return answer
        return None
    return visit(0)


def transferable_slack_parameters(instance, assignment_factor=1., capacity_factor=1.):
    """Rigorous no-optimum-use rule for nonnegative objective/integer residuals."""
    if assignment_factor < 1 or capacity_factor < 1:
        raise ValueError('Factors below one void the sufficient correctness bound')
    c = np.asarray(instance['c'])
    if (c < 0).any() or not np.equal(instance['q'], np.round(instance['q'])).all():
        raise ValueError('Bound requires nonnegative objective and integer demands')
    a = first_feasible_assignment(instance)
    if a is None:
        raise ValueError('No feasible capacity assignment')
    upper = sum(c[i,j] for i,j in itertools.combinations(range(len(a)),2) if a[i] == a[j])
    margin = max(1., 1e-6*upper)
    return {'A': float(assignment_factor*(upper+margin)),
            'W': float(capacity_factor*(upper+margin)),
            'feasible_cost_upper_bound': float(upper), 'strict_margin': float(margin),
            'uses_optimal_reference': False}


def self_check():
    import importlib.util
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location('independent_classical', root/'audit/fidelity/classical_compare/small_exact.py')
    other = importlib.util.module_from_spec(spec); spec.loader.exec_module(other)
    instances = json.loads((root/'audit/scaling/references/instances.json').read_text())['instances']
    checks = []
    for inst in [x for x in instances if x['tier']=='S']:
        n = inst['K']*(inst['N']+len(slack_weights(inst['Q'])))
        z = ((np.arange(1 << n)[:,None] >> np.arange(n))&1).astype(np.int8)
        ours = classify_bits(z, inst, 'slack'); theirs = other.decode(z, inst, 'slack')
        for key in ('assignment_valid','feasible','optimal','cost'):
            assert np.array_equal(ours[key], theirs[key]), key
        p = np.zeros(1 << n); good = np.flatnonzero(ours['optimal_full_encoding'])[0]; p[good] = 1
        assert score_probabilities(p, ours)['optimal'] == 1
        rev = int(format(int(good), f'0{n}b')[::-1], 2)
        assert basis_masks(inst, 'slack', 'big')['optimal'][rev]
        assert basis_masks(inst, 'slack', 'little', True)['optimal'][(1 << n)-1-good]
        pars = transferable_slack_parameters(inst)
        poisoned = dict(inst, f_star=-999999.)
        assert pars == transferable_slack_parameters(poisoned)
        x = z[:, :inst['N']*inst['K']].reshape(-1,inst['K'],inst['N']).transpose(0,2,1)
        loads = np.einsum('i,bik->bk', inst['q'], x)
        helper = z[:,inst['N']*inst['K']:].reshape(-1, inst['K'], len(slack_weights(inst['Q']))) @ slack_weights(inst['Q'])
        energy = ours['cost'] + pars['A']*((x.sum(2)-1)**2).sum(1) + pars['W']*((loads+helper-inst['Q'])**2).sum(1)
        ground = np.isclose(energy, energy.min(), atol=TOL, rtol=0)
        assert ours['optimal_full_encoding'][ground].all()
        checks.append(dict(seed=inst['seed'], states=len(z), scoring_equal=True, transferable_ground_correct=True, penalty_parameters=pars))
    output = dict(passed=True, checks=checks, exhaustive_states=sum(x['states'] for x in checks), conventions_tested=['little','big','zero_is_excited'], oracle_reference_not_used_for_penalties=True)
    (Path(__file__).parent/'formulation_checks.json').write_text(json.dumps(output, indent=2))
    print(json.dumps({'passed':True,'instances':len(checks),'states':output['exhaustive_states']}))

if __name__ == '__main__':
    self_check()
