"""Bounded geometry benchmarks. No objective solution is used by either embedder.

J contains full pair coefficients in its symmetric off-diagonal entries.
eps_J = ||U-alpha J||_F / ||alpha J||_F (off-diagonal only),
with alpha=<U,J>/<J,J>. This is identical to upper-triangle norm ratio.
"""
from __future__ import annotations
import dataclasses
import time
import numpy as np
from scipy.optimize import minimize
from pulser.devices import AnalogDevice, MockDevice

DEVICE = AnalogDevice
C6 = float(DEVICE.interaction_coeff)
R_MIN = float(DEVICE.min_atom_distance)
R_MAX = float(DEVICE.max_radial_distance)
OMEGA_MAX = float(DEVICE.channels['rydberg_global'].max_amp)
DELTA_MAX = float(DEVICE.channels['rydberg_global'].max_abs_detuning)


def loss_gradient(flat, J):
    """Notebook02 objective with its exact analytic derivative."""
    n = len(J); p = np.asarray(flat).reshape(n, 2); ix, iy = np.triu_indices(n, 1)
    diff = p[ix] - p[iy]; d = np.maximum(np.linalg.norm(diff, axis=1), 1e-12)
    j = J[ix, iy]; u = C6 / d**6; jj = j @ j; dot = u @ j; a = dot/jj
    r = u-a*j; rel = np.linalg.norm(r) / (a*np.sqrt(jj))
    du = r / (a*a*jj*max(rel, 1e-15)) - rel*j/dot
    near = np.maximum(R_MIN*1.001-d, 0)
    dd = -6*u/d*du -100*near
    pg = dd[:,None]*diff/d[:,None]
    grad = np.zeros_like(p); np.add.at(grad, ix, pg); np.add.at(grad, iy, -pg)
    centered = p-p.mean(axis=0); radii = np.linalg.norm(centered,axis=1)
    far = np.maximum(radii-R_MAX*.999,0)
    rg = 100*far[:,None]*centered/np.maximum(radii[:,None],1e-12)
    grad += rg-rg.mean(axis=0)
    return float(rel+50*(near@near+far@far)), grad.ravel()


def _physical(p,h,J):
    p = p-p.mean(axis=0); ix=np.triu_indices(len(p),1)
    d = np.linalg.norm(p[:,None]-p[None,:],axis=-1)[ix]
    p *= (R_MIN+1e-3)/d.min()
    d = np.linalg.norm(p[:,None]-p[None,:],axis=-1)[ix]
    j=J[ix]; alpha=(C6/d**6)@j/(j@j)
    p *= max(1.,alpha*np.abs(h).max()/(.95*DELTA_MAX))**(1/6)
    d=np.linalg.norm(p[:,None]-p[None,:],axis=-1)[ix]
    u=C6/d**6; alpha=u@j/(j@j); U=np.zeros_like(J); U[ix]=u; U+=U.T
    radius=float(np.linalg.norm(p,axis=1).max())
    return p,U,float(alpha),float(d.min()),radius


def embed(h,J,method,seed,restarts=8,maxiter=300):
    h=np.asarray(h,dtype=float); J=np.asarray(J,dtype=float).copy(); np.fill_diagonal(J,0)
    if J.shape != (len(h),len(h)) or not np.allclose(J,J.T) or np.any(J<0) or not np.any(J>0):
        raise ValueError('Expected symmetric nonnegative nonzero pair coefficients')
    start=time.perf_counter(); records=[]
    if method=='custom':
        rng=np.random.default_rng(seed); candidates=[]
        for _ in range(restarts):
            t=time.perf_counter()
            r=minimize(loss_gradient,rng.uniform(-10,10,size=2*len(h)),args=(J,),jac=True,
                       method='L-BFGS-B',options={'maxiter':maxiter})
            records.append(dict(success=bool(r.success),message=str(r.message),nit=int(r.nit),nfev=int(r.nfev),loss=float(r.fun),seconds=time.perf_counter()-t))
            candidates.append(r)
        # Same winner selection and physical scaling as the notebook, including failed convergence reporting.
        best=min(candidates,key=lambda x:x.fun); p=best.x.reshape(-1,2)
        optimizer=dict(success=bool(best.success),restarts=restarts,maxiter=maxiter,runs=records)
    elif method.lower()=='blade':
        from qubosolver import Instance, matrix
        from qubosolver.embedding.blade import Config, embed as blade_embed
        from qubosolver.embedding._algorithms.mds import embed_mds
        # Symmetric QUBO convention x^T Q x requires half of full pair coefficients.
        Q=J/2; np.fill_diagonal(Q,h)
        state=np.random.get_state()
        try:
            np.random.seed(seed)
            initial=embed_mds(Q,max_iter=maxiter)
            cfg=Config(starting_positions=initial,initialize_with_mds=False,steps_per_round=200,
                       max_min_dist_ratio=R_MAX/(R_MIN+1e-3))
            reg=blade_embed(Instance(matrix.as_tensor(Q)),config=cfg)
            p=np.asarray([reg.qubits[k] for k in range(len(h))],dtype=float)
        finally:
            np.random.set_state(state)
        optimizer=dict(success=None,message='BLaDE returns coordinates without a convergence certificate',steps_per_round=200,
                       dimensions=list(cfg.dimensions),ratio_rerun=cfg.ratio_rerun,mds_maxiter=maxiter,mds_n_init=4)
    else:
        raise ValueError(method)
    p,U,alpha,dmin,radius=_physical(p,h,J); ix=np.triu_indices(len(h),1); u=U[ix]; j=J[ix]
    spread=float(np.ptp(h)); eps=(h-h.min())/spread if spread else np.zeros(len(h))
    zero=j==0; norm=float(np.linalg.norm(alpha*j)); valid=bool(dmin>=R_MIN-1e-6 and radius<=R_MAX+1e-6)
    return dict(method=method,seed=int(seed),n=len(h),positions=p.tolist(),realized_U=U.tolist(),alpha=alpha,
                eps_J=float(np.linalg.norm(u-alpha*j)/norm),zero_coupling_leakage=float(np.linalg.norm(u[zero])/norm),
                zero_coupling_leakage_max=float(u[zero].max()) if zero.any() else 0.,
                target_density=float(np.mean(j>0)),realized_density=float(np.mean(u>0)),
                realized_density_1pct=float(np.mean(u>=.01*u.max())),density_threshold_fraction=.01,
                physical_valid=valid,min_distance=dmin,max_radius=radius,
                controls=dict(delta_global=float(-alpha*h.mean()),delta_top=float(-alpha*h.min()),
                              dmm_weights=eps.tolist(),delta_dmm=float(-alpha*spread)),
                h=h.tolist(),optimizer=optimizer,seconds=time.perf_counter()-start)


def build_sequence(emb,use_dmm=False,t_ns=4000):
    """Fixed physical pulse; DMM uses virtual device and is explicitly emulator-only."""
    from pulser import Pulse, Sequence
    from pulser.register import RegisterLayout
    from pulser.waveforms import InterpolatedWaveform
    if not emb['physical_valid']:
        raise ValueError('Embedding violates device geometry; cannot construct physical pulse')
    pos=np.asarray(emb['positions']); n=len(pos); traps=list(pos)
    # Satisfy AnalogDevice half-filled layout constraint without changing occupied positions.
    # Fine radial candidates avoid the coarse six-micrometre grid's artificial
    # failure near eighty atoms. Empty traps are physical but unoccupied.
    for radius in np.arange(R_MAX-.01,0,-.25):
        for theta in np.linspace(0,2*np.pi,256,endpoint=False):
            point=radius*np.array([np.cos(theta),np.sin(theta)])
            if len(traps)<2*n and np.linalg.norm(np.asarray(traps)-point,axis=1).min()>=R_MIN+.001:
                traps.append(point)
        if len(traps)>=2*n:
            break
    if len(traps)<2*n:
        raise ValueError('Could not fit enough empty traps for device filling constraint')
    layout=RegisterLayout(np.asarray(traps)); ids=[f'q{i}' for i in range(n)]
    reg=layout.define_register(*layout.get_traps_from_coordinates(*pos),qubit_ids=ids)
    if not np.allclose(np.asarray([reg.qubits[k].as_array() for k in ids]),pos,atol=1e-5):
        raise AssertionError('Variable-to-atom ordering changed')
    device=dataclasses.replace(DEVICE.to_virtual(),dmm_objects=MockDevice.dmm_objects) if use_dmm else DEVICE
    seq=Sequence(reg,device); seq.declare_channel('ising','rydberg_global'); c=emb['controls']
    end=c['delta_top'] if use_dmm else c['delta_global']
    seq.add(Pulse(InterpolatedWaveform(t_ns,[1e-9,OMEGA_MAX,OMEGA_MAX,1e-9]),
                  InterpolatedWaveform(t_ns,[-2*OMEGA_MAX,0,end]),0),'ising')
    if use_dmm:
        seq.config_detuning_map(reg.define_detuning_map(dict(zip(ids,c['dmm_weights']))),'dmm_0')
        seq.add_dmm_detuning(InterpolatedWaveform(t_ns,[0,0,c['delta_dmm']]),'dmm_0')
    return seq
