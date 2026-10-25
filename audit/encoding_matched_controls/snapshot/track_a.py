"""Track A problem code that qubo-solver does not provide: instances, references, QUBO builders, decoding, metrics.

Everything here is copied from notebooks 01 (slack) and 02 (reduced one-hot) so that the qubo-solver notebook (03)
runs on exactly the same seed-12 / seed-9 instances and the same QUBOs. Conventions: E(z) = z.h + 1/2 z.J.z + const,
J symmetric with zero diagonal; qubo-solver's cost is x^T Q x, so Q = diag(h) + J / 2.
"""

from __future__ import annotations

import itertools

import numpy as np

DEPOT = np.array([50.0, 50.0])
TIERS = {"S": dict(N=4, K=2, Q=7, qmax=4), "M": dict(N=10, K=3, Q=20, qmax=8)}
SEED = 7


# ---------------------------------------------------------------- instances and brute-force references

def make_instance(N, qmax, seed):
    rng = np.random.default_rng(seed)
    return rng.uniform(0, 100, size=(N, 2)), rng.integers(1, qmax + 1, size=N)


def assignment_table(N, K, xy, q, Q):
    """All K^N assignments with their clustering cost f and loads (vectorised)."""
    A = np.array(list(itertools.product(range(K), repeat=N)), dtype=np.int8)
    c = np.linalg.norm(xy[:, None] - xy[None, :], axis=-1)
    same = A[:, :, None] == A[:, None, :]
    f = (same * np.triu(c, 1)).sum(axis=(1, 2))
    L = np.stack([(q * (A == k)).sum(1) for k in range(K)], axis=1)
    return A, f, L, c


def canon(assign, K):
    """Clustering as a set of customer groups, so relabelled trucks compare equal (brief Pitfall 9.3)."""
    return frozenset(frozenset(np.flatnonzero(assign == k).tolist()) for k in range(K) if (assign == k).any())


def cluster_cost(assign, c):
    same = assign[:, None] == assign[None, :]
    return float(np.triu(c * same, 1).sum())


def held_karp(xy):
    """Exact depot-to-depot TSP for every customer subset (bitmask), O(2^N N^2). Returns (cost[mask], tour(mask))."""
    N = len(xy)
    d0 = np.linalg.norm(xy - DEPOT, axis=1)
    d = np.linalg.norm(xy[:, None] - xy[None, :], axis=-1)
    dp = np.full((1 << N, N), np.inf)
    parent = np.full((1 << N, N), -1, dtype=int)
    for i in range(N):
        dp[1 << i, i] = d0[i]
    for mask in range(1, 1 << N):
        for last in range(N):
            if not (mask >> last) & 1 or np.isinf(dp[mask, last]):
                continue
            for nxt in range(N):
                if (mask >> nxt) & 1:
                    continue
                m2, v = mask | (1 << nxt), dp[mask, last] + d[last, nxt]
                if v < dp[m2, nxt]:
                    dp[m2, nxt], parent[m2, nxt] = v, last
    close = dp + d0[None, :]
    cost = np.where(np.arange(1 << N) == 0, 0.0, close.min(1))

    def tour(mask):
        if mask == 0:
            return ()
        last, out = int(np.argmin(close[mask])), []
        while last >= 0:
            out.append(last)
            mask, last = mask ^ (1 << last), parent[mask, last]
        return tuple(reversed(out))

    return cost, tour


def route_assignment(I, assign):
    """Route each cluster exactly (Held-Karp table); return (routes, total length)."""
    masks = [int(sum(1 << i for i in np.flatnonzero(assign == k))) for k in range(I["K"])]
    return [I["tour"](m) for m in masks], float(sum(I["tsp"][m] for m in masks))


def instance_from_seed(tier, seed):
    """The tier's instance for this seed with brute-force references, or None unless it is feasible with capacity
    active (the best split ignoring capacity overloads a truck), the filter of notebooks 01/02."""
    P = TIERS[tier]
    xy, q = make_instance(P["N"], P["qmax"], seed)
    A, f, L, c = assignment_table(P["N"], P["K"], xy, q, P["Q"])
    feas = L.max(1) <= P["Q"]
    if not feas.any() or f[feas].min() <= f.min() + 1e-9:
        return None
    f_star = f[feas].min()
    opt = {canon(a, P["K"]) for a in A[feas & np.isclose(f, f_star)]}
    # certificate: the first feasible assignment in enumeration order, as in notebook 01
    I = dict(P, tier=tier, seed=seed, xy=xy, q=q, c=c, A=A, f=f, L=L, feas=feas, f_star=f_star, opt=opt,
             x_star=A[feas & np.isclose(f, f_star)][0], certificate=A[feas][0])
    I["tsp"], I["tour"] = held_karp(xy)
    masks = np.stack([(A == k).astype(np.int64) @ (1 << np.arange(P["N"])) for k in range(P["K"])], axis=1)
    cvrp = np.where(feas, I["tsp"][masks].sum(1), np.inf)
    I["cvrp_ref"], I["cvrp_ref_assign"] = float(cvrp.min()), A[int(np.argmin(cvrp))]
    return I


def capacity_active_seeds(tier, count, start=SEED):
    """The first `count` seeds from `start` whose instance passes the filter."""
    seeds, seed = [], start
    while len(seeds) < count:
        if instance_from_seed(tier, seed) is not None:
            seeds.append(seed)
        seed += 1
    return seeds


def load_instances():
    """Notebook 01/02 seed search: from SEED, the first instance per tier that passes the filter."""
    return {tier: instance_from_seed(tier, capacity_active_seeds(tier, 1)[0]) for tier in TIERS}


# ---------------------------------------------------------------- encoding 1: reduced one-hot (notebook 02)

def _indicator(i, k, K):
    """y_ik as (constant, {bit: coef}): truck 0 = 1 - sum_u z_iu, truck k>0 = z_i,k-1."""
    bits = [i * (K - 1) + u for u in range(K - 1)]
    return (1.0, {b: -1.0 for b in bits}) if k == 0 else (0.0, {bits[k - 1]: 1.0})


def _add_product(h, J, e1, e2, w):
    """Add w * e1 * e2 to (h, J); return the constant part. Uses z^2 = z."""
    (c1, l1), (c2, l2) = e1, e2
    const = w * c1 * c2
    for b, v in l1.items():
        h[b] += w * v * c2
    for b, v in l2.items():
        h[b] += w * v * c1
    for (a, va), (b, vb) in itertools.product(l1.items(), l2.items()):
        if a == b:
            h[a] += w * va * vb
        else:
            J[a, b] += w * va * vb
            J[b, a] += w * va * vb
    return const


def build_onehot_qubo(I, M, mu):
    """E(z) = f(y) + M*(invalid pairs) + mu * sum_k (L_k - Q)^2, K-1 bits per customer."""
    N, K, Q, q, c = I["N"], I["K"], I["Q"], I["q"], I["c"]
    n = N * (K - 1)
    h, J, const = np.zeros(n), np.zeros((n, n)), 0.0
    for k in range(K):
        for i, j in itertools.combinations(range(N), 2):
            const += _add_product(h, J, _indicator(i, k, K), _indicator(j, k, K), c[i, j])
    for i in range(N):
        for u, v in itertools.combinations(range(K - 1), 2):
            a, b = i * (K - 1) + u, i * (K - 1) + v
            J[a, b] += M
            J[b, a] += M
    for k in range(K):
        load = (-Q, {})
        for i in range(N):
            ci, li = _indicator(i, k, K)
            load = (load[0] + q[i] * ci, {**load[1], **{b: load[1].get(b, 0) + q[i] * v for b, v in li.items()}})
        const += _add_product(h, J, load, load, mu)
    return h, J, const


def m_bound(I, mu):
    """Smallest M for which dropping one bit of a doubly-set customer always lowers the energy (notebook 02 §3)."""
    D, q, s = I["q"].sum(), I["q"], I["c"].sum(1)
    return float(np.ceil(np.max(s + 2 * mu * q * (D - 2 * q)))) + 1.0 if I["K"] > 2 else 0.0


def choose_mu(I, coupling_max, detuning_max, mus=np.geomspace(1e-2, 1e2, 81)):
    """Notebook 02 rule: maximise (QUBO margin of the optimum) x (device scale alpha the coefficients allow)."""
    not_opt = np.array([canon(a, I["K"]) not in I["opt"] for a in I["A"]])
    best = (-np.inf, None)
    for mu in mus:
        E = I["f"] + mu * ((I["L"] - I["Q"]) ** 2).sum(1)
        margin = E[not_opt].min() - E[~not_opt].min()
        h, J, _ = build_onehot_qubo(I, m_bound(I, mu), mu)
        alpha = min(coupling_max / J.max(), 0.95 * detuning_max / np.abs(h).max())
        if margin > 0 and margin * alpha > best[0]:
            best = (margin * alpha, mu)
    return best[1]


def mu_equal_weight(I):
    """A mu that uses only instance data: weight distance and balance equally in the same-truck pair coupling
    J = 2 c_ij + 4 mu q_i q_j, i.e. mu = mean(2 c_ij) / mean(4 q_i q_j) over pairs. Unlike `choose_mu` it does not
    look at the optimum, so it can fail to make the optimum the QUBO's minimum."""
    iu = np.triu_indices(I["N"], 1)
    return float(np.mean(2 * I["c"][iu]) / np.mean(4 * np.outer(I["q"], I["q"])[iu]))


def decode_onehot(z, I):
    """Return (assignment or None if a code is invalid, valid_code, feasible)."""
    K, N = I["K"], I["N"]
    Zc = np.asarray(z).reshape(N, K - 1)
    if (Zc.sum(1) > 1).any():
        return None, False, False
    assign = np.where(Zc.any(1), Zc.argmax(1) + 1, 0)
    loads = np.array([I["q"][assign == k].sum() for k in range(K)])
    return assign, True, bool(loads.max() <= I["Q"])


# ---------------------------------------------------------------- encoding 2: one-hot + binary slack (notebook 01)

def slack_weights(Q):
    B = int(np.ceil(np.log2(Q + 1)))
    w = [2 ** b for b in range(B - 1)]
    return np.array(w + [Q - sum(w)])


def build_slack_qubo(I, A, W):
    """E = f(x) + A sum_i (sum_k x_ik - 1)^2 + W sum_k (sum_i q_i x_ik + sum_b w_b y_kb - Q)^2.
    Bits: x[k*N + i], then y[N*K + k*B + b]."""
    N, K, Q, q, c = I["N"], I["K"], I["Q"], I["q"], I["c"]
    w = slack_weights(Q)
    B, n_x = len(w), N * K
    n = n_x + K * B
    h, J, const = np.zeros(n), np.zeros((n, n)), 0.0

    def add(a, b, v):
        if a == b:
            h[a] += v
        else:
            J[a, b] += v
            J[b, a] += v

    for k in range(K):
        for i, j in itertools.combinations(range(N), 2):
            add(k * N + i, k * N + j, c[i, j])
    for i in range(N):
        for k in range(K):
            add(k * N + i, k * N + i, -A)
        for k, l in itertools.combinations(range(K), 2):
            add(k * N + i, l * N + i, 2 * A)
        const += A
    for k in range(K):
        terms = [(k * N + i, q[i]) for i in range(N)] + [(n_x + k * B + b, w[b]) for b in range(B)]
        for idx, a in terms:
            add(idx, idx, W * (a * a - 2 * Q * a))
        for (p, a), (r, b) in itertools.combinations(terms, 2):
            add(p, r, 2 * W * a * b)
        const += W * Q * Q
    return h, J, const


def decode_slack(z, I):
    """Drop slack bits; return (assignment or None if a customer is not on exactly one truck, C1 ok, feasible)."""
    N, K = I["N"], I["K"]
    X = np.asarray(z[:N * K]).reshape(K, N)
    if not (X.sum(0) == 1).all():
        return None, False, False
    assign = X.argmax(0)
    loads = np.array([I["q"][assign == k].sum() for k in range(K)])
    return assign, True, bool(loads.max() <= I["Q"])


# ---------------------------------------------------------------- shared helpers and metrics

def energies(Z, h, J, chunk=1 << 16):
    out = np.empty(len(Z))
    for s in range(0, len(Z), chunk):
        Zf = Z[s:s + chunk].astype(np.float64)
        out[s:s + chunk] = Zf @ h + 0.5 * np.einsum("ri,ij,rj->r", Zf, J, Zf)
    return out


def score(bitstrings, counts, I, decode):
    """Brief §9.4 metrics on raw shots (no repair): feasibility rate, P(reach ref) with eps = 0, model and CVRP gap
    of the best feasible shot. `bitstrings` is (rows, n) of 0/1, `counts` the shots per row."""
    counts = np.asarray(counts, float)
    feas, ref, best = np.zeros(len(counts), bool), np.zeros(len(counts), bool), (np.inf, None)
    for r, z in enumerate(bitstrings):
        a, _, ok = decode(np.asarray(z, int), I)
        if ok:
            feas[r] = True
            f = cluster_cost(a, I["c"])
            ref[r] = canon(a, I["K"]) in I["opt"]
            if f < best[0]:
                best = (f, a)
    out = {"shots": int(counts.sum()), "feasibility rate": counts[feas].sum() / counts.sum(),
           "P(reach ref)": counts[ref].sum() / counts.sum(), "model gap %": np.nan, "CVRP gap %": np.nan}
    if best[1] is not None:
        out["model gap %"] = (best[0] - I["f_star"]) / I["f_star"] * 100
        out["CVRP gap %"] = (route_assignment(I, best[1])[1] - I["cvrp_ref"]) / I["cvrp_ref"] * 100
    return out


def coupling_error(coords, J):
    """||U - aJ||_F / ||aJ||_F over all pairs, U = 1/r^6, a fitted in closed form (scale-free, so units do not
    matter). Same formula as notebooks 01 and 02."""
    iu = np.triu_indices(len(J), 1)
    U = 1.0 / np.linalg.norm(coords[:, None] - coords[None], axis=-1)[iu] ** 6
    Jp = J[iu]
    a = U @ Jp / (Jp @ Jp)
    return float(np.linalg.norm(U - a * Jp) / np.linalg.norm(a * Jp))
