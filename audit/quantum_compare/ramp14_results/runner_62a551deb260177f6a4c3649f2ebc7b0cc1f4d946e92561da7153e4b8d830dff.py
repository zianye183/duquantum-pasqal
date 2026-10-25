"""Resumable bounded matched intended/geometric Pasqal runner. Preparation is local; --submit opts into cloud.
Inputs: prepared/<id>/{sequence.json,config.json,metadata.json}; metadata backend,
shots. Counts retain Pulser's result atom order without decoding/reordering.
A submission with an uncertain outcome is NEVER automatically repeated.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
import signal
from pathlib import Path
import sys
import time
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
sys.path.insert(0, str(REPO / 'notebooks'))


def now():
    return datetime.datetime.now(ZoneInfo('America/New_York')).isoformat()


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    with tmp.open('w') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    tmp.replace(path)


def event(out, row):
    with (out / 'journal.jsonl').open('a') as f:
        f.write(json.dumps(dict(at=now(), **row)) + '\n')
        f.flush()
        os.fsync(f.fileno())


def safe_error(exc):
    # Remote errors can contain credentials/URLs; retain type only by default.
    return {'type': type(exc).__name__, 'detail': 'Remote exception text withheld; inspect authenticated service for detail.'}


def load_job(path):
    from pulser import Sequence
    from pulser.backend import EmulationConfig, BitStrings
    raw = {name: (path / (name + '.json')).read_text() for name in ['sequence', 'config', 'metadata']}
    meta = json.loads(raw['metadata'])
    seq = Sequence.from_abstract_repr(raw['sequence'])
    cfg = EmulationConfig.from_abstract_repr(raw['config'])
    backend = meta['backend']
    assert backend in ['cloud-sv', 'cloud-mps'], backend
    config_changes = {}
    if backend == 'cloud-mps':
        from pasqal_cloud import RemoteMPSBackend
        before = json.loads(cfg.to_abstract_repr())
        cfg = RemoteMPSBackend.validate_config(cfg)
        after = json.loads(cfg.to_abstract_repr())
        assert all(after[k] == v for k, v in before.items()), 'Official validation changed an explicit option'
        config_changes = {k: v for k, v in after.items() if k not in before}
        assert set(config_changes) <= {'num_gpus_to_use', 'autosave_dt', 'optimize_qubit_ordering'}
    mode = meta['interaction_mode']
    assert mode in {'intended', 'geometric'}
    assert (cfg.interaction_matrix is None) == (mode == 'geometric'), 'Interaction mode/config mismatch'
    if mode == 'intended':
        import numpy as np
        matrix = np.asarray(cfg.interaction_matrix.as_array(detach=True), dtype=float)
        if matrix.ndim == 3 and matrix.shape[0] == 1:
            matrix = matrix[0]  # Pulser canonical single-Hamiltonian batch axis.
        assert matrix.shape == (len(seq.register.qubits), len(seq.register.qubits))
        assert np.isfinite(matrix).all() and np.allclose(matrix, matrix.T)
        assert np.allclose(np.diag(matrix), 0), 'Pair matrix must have zero diagonal'
    n = len(seq.register.qubits)
    assert n <= (20 if backend == 'cloud-sv' else 80), n
    assert not seq.is_parametrized() and not seq.is_register_mappable()
    shots = int(meta.get('shots', 2000))
    obs = [o for o in cfg.observables if isinstance(o, BitStrings)]
    assert len(obs) == 1 and obs[0].num_shots == shots
    assert list(obs[0].evaluation_times) == [1.0]
    if not seq.is_measured():
        seq.measure('ground-rydberg')
    digest = hashlib.sha256(''.join(raw.values()).encode()).hexdigest()
    return dict(id=path.name, meta=meta, sequence=seq, config=cfg, digest=digest,
                atom_order=list(seq.register.qubits), shots=shots, config_changes=config_changes)


def validate_frozen(prepared):
    """Refuse incomplete, altered or unmatched scientific inputs before HTTP."""
    manifest = json.loads((prepared / 'FROZEN_MANIFEST.json').read_text())
    expected = {j['id']: j['digest'] for j in manifest['jobs']}
    assert len(expected) == len(manifest['jobs']) and expected
    pairs = {}
    for name, digest in expected.items():
        path = prepared / name
        raw = [(path / (part + '.json')).read_text() for part in ['sequence', 'config', 'metadata']]
        assert hashlib.sha256(''.join(raw).encode()).hexdigest() == digest, 'Prepared bytes changed'
        meta = json.loads(raw[2])
        cfg = json.loads(raw[1])
        mode = meta['interaction_mode']
        assert mode in {'intended', 'geometric'}
        pair = pairs.setdefault(meta['pair_id'], {})
        assert mode not in pair, 'Duplicate arm'
        cfg.pop('interaction_matrix', None)
        pair[mode] = (json.loads(raw[0]), cfg, meta['backend'], meta['shots'])
    for pair in pairs.values():
        assert set(pair) == {'intended', 'geometric'}, 'Missing matched arm'
        assert pair['intended'] == pair['geometric'], 'Matched arms differ beyond interactions'
    discovered = {p.name for p in prepared.iterdir() if p.is_dir() and (p/'metadata.json').exists()}
    assert discovered == set(expected), 'Manifest must cover every prepared input'
    return expected


def readiness():
    """Authenticated read-only project/device inspection; never submits work."""
    from emulation import cloud_connection, _load_env_file
    from pasqal_cloud.device import DeviceTypeName
    _load_env_file(Path('/Users/alanye/duquantum-pasqal/.env'))
    report = {'observed_at': now(), 'read_only': True, 'submitted_jobs': 0,
              'sdk_emulator_types': [str(x) for x in DeviceTypeName if str(x).startswith('EMU')],
              'cost': 'No pricing or charge accessor in inspected SDK; cost unavailable.',
              'backend_access': 'SDK support alone does not confirm execution entitlement.'}
    try:
        conn = cloud_connection()
        projects = conn.cloud_client.get_all_projects()
        current = [p for p in projects if p.id == conn.cloud_client.project_id]
        devices = conn.fetch_available_devices()
        report.update(authenticated=True, configured_project_accessible=bool(current),
                      device_specifications=list(devices), accessible_project_count=len(projects))
        # Retain key names only; unknown project extras may include private values.
        report['configured_project_extra_field_names'] = sorted((current[0].model_extra or {}).keys()) if current else []
        if current:
            extra = current[0].model_extra or {}
            report['allowed_device_types'] = extra.get('allowed_device_types')
            report['max_concurrent_job'] = extra.get('max_concurrent_job')
            report['backend_access'] = 'Project allowed_device_types read from authenticated service; execution not yet tested.'
    except Exception as exc:
        report.update(authenticated=False, error=safe_error(exc))
    write(ROOT / 'cloud_readiness.json', report)
    print(json.dumps(report), flush=True)


def run(args):
    from emulation import cloud_connection, _load_env_file
    _load_env_file(Path('/Users/alanye/duquantum-pasqal/.env'))
    from pasqal_cloud.device import DeviceTypeName
    from pulser.backend.remote import RemoteResults
    assert not args.watch_preparation, 'Matched experiments require frozen preparation'
    args.output.mkdir(parents=True, exist_ok=True)
    source = Path(__file__).read_bytes()
    source_digest = hashlib.sha256(source).hexdigest()
    source_path = args.output / ('runner_' + source_digest + '.py')
    if not source_path.exists():
        source_path.write_bytes(source)
    lock = (args.output / 'runner.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    stopping = [False]
    def request_stop(signum, frame):
        stopping[0] = True  # Finish any current HTTP request and journal its handle.
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    recovered = {}
    if (args.output / 'journal.jsonl').exists():
        for line in (args.output / 'journal.jsonl').read_text().splitlines():
            item = json.loads(line)
            if item.get('batch_id'):
                recovered[item['id']] = item
    states, jobs, discovered = {}, [], set()
    def discover():
        for path in sorted(args.prepared.glob('*')):
            if path.name in discovered or not (path / 'metadata.json').exists():
                continue
            if args.only and path.name not in args.only:
                continue
            try:
                meta = json.loads((path / 'metadata.json').read_text())
                if args.watch_preparation and meta.get('status') != 'ready':
                    continue
                j = load_job(path)
                state_path = args.output / j['id'] / 'state.json'
                state = json.loads(state_path.read_text()) if state_path.exists() else dict(id=j['id'], status='ready', digest=j['digest'])
                assert state['digest'] == j['digest'], 'Prepared input changed after submission'
                if not state.get('batch_id') and j['id'] in recovered:
                    state.update(batch_id=recovered[j['id']]['batch_id'], status='submitted')
                if state['status'] == 'submitting' and not state.get('batch_id'):
                    state['status'] = 'submission_unknown'
                states[j['id']] = state
                write(state_path, state)
                jobs.append(j)
            except Exception as exc:
                state = dict(id=path.name, status='invalid_input', error=safe_error(exc), observed_at=now())
                states[path.name] = state
                write(args.output / path.name / 'input_error.json', state)
            discovered.add(path.name)
    def apply_aliases():
        path = args.prepared / 'ALIASES.json'
        if not path.exists():
            return
        for alias in json.loads(path.read_text()).get('aliases', []):
            if alias['id'] not in states:
                continue
            state = states[alias['id']]
            if state.get('batch_id'):
                raise RuntimeError('Cannot alias an already-submitted job')
            if state['status'] not in {'ready', 'alias'}:
                raise RuntimeError('Alias requires a ready unsubmitted input')
            state.update(status='alias', alias_of=alias['alias_of'],
                         alias_equivalence=alias.get('equivalence'), independent_evidence=False)
            write(args.output / alias['id'] / 'state.json', state)
    frozen = validate_frozen(args.prepared)
    discover()
    assert len(states) == len(jobs), 'Some frozen inputs invalid; refuse partial paired submission'
    for job in jobs:
        assert frozen[job['id']] == job['digest'], 'Frozen digest mismatch'
    apply_aliases()
    print(json.dumps({'validated': len(jobs), 'input_errors':len(states)-len(jobs), 'submit': args.submit}), flush=True)
    if args.validate_only:
        if len(states) != len(jobs):
            raise ValueError('Prepared input validation failed; inspect input_error.json')
        return
    if not jobs and not args.watch_preparation:
        raise ValueError('No prepared jobs selected')
    connection = cloud_connection()
    # Prevent the SDK's HTTP-status retry policy from duplicating a POST.
    client = connection.cloud_client._client
    original_request = client._request_with_status_check
    def no_post_retry(method, *a, **kw):
        try:
            return original_request(method, *a, **kw)
        except Exception as exc:
            if method == 'POST':
                raise RuntimeError('Uncertain POST outcome; manual reconciliation required') from exc
            raise
    client._request_with_status_check = no_post_retry
    start = time.monotonic()
    terminal = {'completed', 'failed', 'submission_unknown', 'invalid_result', 'invalid_input', 'alias'}
    while True:
        if args.watch_preparation:
            discover()
        apply_aliases()
        for j in jobs:
            if stopping[0]:
                break
            s = states[j['id']]
            dest = args.output / j['id']
            if not s.get('batch_id') or s['status'] in terminal:
                continue
            try:
                remote = RemoteResults(s['batch_id'], connection)
                status = str(remote.get_batch_status())
                s.update(remote_status=status, last_observed_at=now())
                if any(x in status.upper() for x in ['ERROR', 'CANCEL', 'TIMED_OUT']):
                    s.update(status='failed', finished_at=now())
                    write(dest / 'state.json', s)
                    continue
                if 'DONE' in status.upper():
                    # A batch can be DONE while its single job is ERROR.
                    batch = connection.cloud_client.get_batch(s['batch_id'])
                    job_counts = batch.jobs_count_per_status
                    s['remote_job_status_counts'] = job_counts
                    if any(job_counts.get(k, 0) for k in ['ERROR', 'CANCELED', 'CANCELING', 'TIMED_OUT']):
                        s.update(status='failed', finished_at=now(),
                                 error={'type':'RemoteJobFailure', 'detail':'Batch completed with a failed job; scientific results unavailable.'})
                        event(args.output, dict(id=j['id'], status='failed', batch_id=s['batch_id']))
                        write(dest / 'state.json', s)
                        continue
                results = remote.get_available_results() if 'DONE' in status.upper() else {}
                if results:
                    assert len(results) == 1, 'Expected exactly one job per batch'
                    result = next(iter(results.values()))
                    counts = {str(k): int(v) for k, v in result.get_result('bitstrings', 1.0).items()}
                    order = list(result.atom_order)
                    assert set(order) == set(j['atom_order']), 'Atom membership mismatch'
                    assert sum(counts.values()) == j['shots'], 'Shot count mismatch'
                    assert all(len(b) == len(order) and set(b) <= {'0','1'} and c >= 0 for b,c in counts.items())
                    write(dest / 'counts.json', counts)
                    s.update(status='completed', finished_at=now(), shots=sum(counts.values()),
                             result_atom_order=order, sequence_atom_order=j['atom_order'])
                    event(args.output, dict(id=j['id'], status='completed', batch_id=s['batch_id']))
                # DONE with temporarily unavailable results remains observable.
            except AssertionError as exc:
                s.update(status='invalid_result', error=str(exc), observed_at=now())
            except Exception as exc:
                s.update(last_observation_error=safe_error(exc), last_observation_error_at=now())
            write(dest / 'state.json', s)
        active = sum(s.get('batch_id') is not None and s['status'] not in terminal for s in states.values())
        uncertain = sum(s['status'] == 'submission_unknown' for s in states.values())
        pending = [j for j in jobs if states[j['id']]['status'] == 'ready']
        while args.submit and not stopping[0] and pending and active + uncertain < args.max_active:
            live = [j for j in jobs if states[j['id']]['status'] not in (terminal - {'submission_unknown'}) | {'ready'}]
            mps_active = sum(j['meta']['backend']=='cloud-mps' for j in live)
            candidates = [j for j in pending if j['meta']['backend']!='cloud-mps' or mps_active < args.max_active_mps]
            if not candidates:
                break
            # Spread current jobs across tiers; prefer SV and primary over accuracy.
            j = min(candidates, key=lambda j: (
                sum(x['meta'].get('tier')==j['meta'].get('tier') for x in live),
                j['meta']['backend']!='cloud-sv',
                j['meta'].get('cohort','primary')!='primary', j['id']))
            pending.remove(j)
            s = states[j['id']]
            dest = args.output / j['id']
            effective = j['config'].to_abstract_repr()
            effective_hash = hashlib.sha256(effective.encode()).hexdigest()
            dest.mkdir(parents=True, exist_ok=True)
            (dest / 'submitted_config.json').write_text(effective)
            (dest / 'submitted_sequence.json').write_text(j['sequence'].to_abstract_repr())
            write(dest / 'submission_provenance.json', dict(prepared_digest=j['digest'], runner_sha256=source_digest,
                  submitted_sequence_sha256=hashlib.sha256(j['sequence'].to_abstract_repr().encode()).hexdigest(),
                  submitted_config_sha256=effective_hash,
                  official_mps_validation=j['meta']['backend']=='cloud-mps',
                  added_defaults={k: 'Infinity' if v == float('inf') else v for k,v in j['config_changes'].items()},
                  explicit_config_options_unchanged=True))
            s.update(submitted_config_sha256=effective_hash)
            s.update(status='submitting', submitted_at=now())
            write(dest / 'state.json', s)
            event(args.output, dict(id=j['id'], status='submitting', digest=j['digest']))
            try:
                # Direct SDK avoids connection.submit retry wrapper and its post-submit GET.
                batch = connection.cloud_client.create_batch(
                    serialized_sequence=j['sequence'].to_abstract_repr(), jobs=[{}],
                    device_type=DeviceTypeName.EMU_SV if j['meta']['backend']=='cloud-sv' else DeviceTypeName.EMU_MPS,
                    backend_configuration=effective, wait=False, open=False,
                    tags=['matched-quantum-audit', j['id']])
                # Journal the server handle BEFORE any further network request.
                event(args.output, dict(id=j['id'], status='submitted', batch_id=batch.id, digest=j['digest']))
                s.update(batch_id=batch.id, status='submitted')
                active += 1
            except Exception as exc:
                s.update(status='submission_unknown', error=safe_error(exc))
                uncertain += 1
            write(dest / 'state.json', s)
            print(json.dumps({'id':j['id'], 'status':s['status']}), flush=True)
        summary = dict(at=now(), total=len(jobs), states={k:sum(s['status']==k for s in states.values()) for k in sorted({s['status'] for s in states.values()})},
                       cost='Unavailable from inspected SDK batch schema; no zero-cost assertion')
        write(args.output / 'summary.json', summary)
        print(json.dumps(summary), flush=True)
        if stopping[0]:
            event(args.output, dict(status='observer_stopped_after_current_request'))
            break
        preparation_done = not args.watch_preparation or (args.prepared / 'PREPARATION_COMPLETE.json').exists()
        if preparation_done and (all(s['status'] in terminal for s in states.values()) or (not args.submit and not active)):
            break
        if args.run_seconds and time.monotonic()-start >= args.run_seconds:
            break  # Observation timeout leaves live jobs and handles intact.
        time.sleep(args.poll_seconds)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, default=ROOT/'prepared')
    p.add_argument('--output', type=Path, default=ROOT/'cloud_results')
    p.add_argument('--submit', action='store_true')
    p.add_argument('--validate-only', action='store_true')
    p.add_argument('--watch-preparation', action='store_true')
    p.add_argument('--only', nargs='+')
    p.add_argument('--max-active', type=int, choices=range(1,9), default=4)
    p.add_argument('--max-active-mps', type=int, choices=range(0,9), default=4)
    p.add_argument('--poll-seconds', type=float, default=20)
    p.add_argument('--run-seconds', type=float, default=0)
    p.add_argument('--readiness', action='store_true')
    args = p.parse_args()
    if args.readiness:
        readiness()
    else:
        run(args)
