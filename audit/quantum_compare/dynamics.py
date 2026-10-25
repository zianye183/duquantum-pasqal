"""Full-state unitary evolution, no shots, truncation, or geometry assumptions.
Basis integer bit i is logical variable i; ground is all-zero. Units rad/us, us.
J is symmetric with each full unordered-pair coefficient in both triangles.
"""
from dataclasses import dataclass, asdict
import time
import numpy as np

@dataclass(frozen=True)
class Pulse:
    duration: float = 4.0
    omega: float = 4.0
    initial_detuning: float = -8.0
    ramp_power: float = 1.0
    drive_power: float = 1.0
    def validate(self):
        if not np.all(np.isfinite(list(asdict(self).values()))) or self.duration<=0 or not 0<=self.omega<=4*np.pi or not -125.66370614359172<=self.initial_detuning<0 or self.ramp_power<=0 or self.drive_power<=0:
            raise ValueError('Invalid pulse or exceeds conservative amplitude/detuning limits')

class DiagonalProblem:
    def __init__(self,h,J):
        h=np.asarray(h,float);J=np.asarray(J,float);n=len(h)
        if n<1:raise ValueError('At least one bit required')
        if n>22:raise ValueError('Full state explicitly limited to <=22 bits')
        if J.shape!=(n,n) or not np.allclose(J,J.T) or not np.allclose(np.diag(J),0) or not np.all(np.isfinite(h)) or not np.all(np.isfinite(J)):
            raise ValueError('Finite symmetric zero-diagonal full-pair matrix required')
        self.h=h;self.J=J;self.n=n
        labels=np.arange(1<<n,dtype=np.uint32)
        self.number=np.zeros(1<<n);self.linear=np.zeros(1<<n);self.pairs=np.zeros(1<<n)
        bits=[((labels>>i)&1).astype(float) for i in range(n)]
        for i in range(n):
            self.number+=bits[i];self.linear+=h[i]*bits[i]
            for j in range(i+1,n):self.pairs+=J[i,j]*bits[i]*bits[j]
    def diagonal(self,s,pulse):
        # Interactions are ALWAYS ON, including at t=0. The individual fields
        # interpolate from positive excitation cost to h_i=-Delta_i at endpoint.
        ramp=s**pulse.ramp_power
        return self.pairs+(1-ramp)*(-pulse.initial_detuning)*self.number+ramp*self.linear
    def amplitude(self,s,pulse):
        return pulse.omega*np.sin(np.pi*s)**pulse.drive_power

def rotate_x(state,angle,n):
    """Apply exp(-i angle sum_i X_i), exploiting mutually commuting X_i."""
    c=np.cos(angle);s=-1j*np.sin(angle)
    for i in range(n):
        view=state.reshape(-1,2,1<<i)
        a=view[:,0,:].copy();b=view[:,1,:].copy()
        view[:,0,:]=c*a+s*b;view[:,1,:]=s*a+c*b

def evolve(problem,pulse,dt=0.01,initial=None,return_state=False):
    """Midpoint Strang splitting. Finite dt approximation, NOT exact time integration.
    Both pairs must use same pulse, fields, step count, and initial state.
    """
    pulse.validate()
    if np.max(np.abs(problem.h))>125.66370614359172+1e-8:raise ValueError('Endpoint field exceeds detuning limit')
    if not np.isfinite(dt) or dt<=0:raise ValueError('dt must be positive')
    steps=int(np.ceil(pulse.duration/dt));step=pulse.duration/steps
    psi=np.zeros(1<<problem.n,dtype=complex) if initial is None else np.array(initial,dtype=complex,copy=True)
    if initial is None:psi[0]=1
    if psi.shape!=(1<<problem.n,) or not np.all(np.isfinite(psi)) or abs(np.vdot(psi,psi).real-1)>1e-10:raise ValueError('Normalized initial state required')
    start=time.monotonic()
    for k in range(steps):
        s=(k+.5)/steps;phase=np.exp(-.5j*step*problem.diagonal(s,pulse))
        psi*=phase;rotate_x(psi,.5*step*problem.amplitude(s,pulse),problem.n);psi*=phase
    prob=abs(psi)**2
    out=dict(probabilities=prob,norm=float(prob.sum()),steps=steps,dt=step,seconds=time.monotonic()-start,pulse=asdict(pulse))
    if return_state:out['state']=psi
    return out

def metrics(probabilities,masks):
    p=np.asarray(probabilities,float)
    out={k:float(p[np.asarray(v,bool)].sum()) for k,v in masks.items() if v is not None and k in ['feasible','optimal','assignment_valid']}
    if masks.get('helper_exact') is not None:
        out['helper_exact']=float(p[np.asarray(masks['helper_exact'],bool)&np.asarray(masks['feasible'],bool)].sum())
    return out
