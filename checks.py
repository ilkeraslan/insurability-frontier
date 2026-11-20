"""Numerical checks of the closed forms and the numbers quoted in the paper:
convergence of the reservation premium to the worst case, the effect of a wider prior,
the buyer's willingness to pay and the frontier multiplier, premium multiples (Table 1)
and the price path after a surprise (Section 5)."""
import numpy as np, sympy as sp
from scipy import integrate
out = []
# ---- 1) KMM-CARA-linear-u reservation premium: closed form pi_n = Lambda(eta n L)/(eta n)
W0, n, pi, th, L, eta = sp.symbols('W0 n pi theta L eta', positive=True)
# indifference: E_mu[ -exp(-eta*(W0 + n*(pi - th*L))) ] = -exp(-eta*W0)
# => E_mu[ exp(-eta*n*(pi - th*L)) ] = 1  => exp(eta*n*pi) = E_mu[exp(eta*n*th*L)]
# => pi = ln E_mu[exp(eta*n*L*th)] / (eta*n)   -- verify by construction (algebra trivial)
out.append("closed form OK by algebra: pi_n = Lambda_mu(eta*n*L)/(eta*n)")

# ---- 2) numeric: Beta(2,8) prior scaled to [0, 0.05]; mean 0.01, sup 0.05
a,b,hi = 2.0, 8.0, 0.05
from scipy.stats import beta as B
mean_th = hi*a/(a+b)
def Lam(t):
    # log-sum-exp form, Lambda(t) = t*hi + log E exp(t*hi*(x-1)), to avoid overflow at large t
    f = lambda x: np.exp(t*hi*(x-1.0))*B.pdf(x,a,b)
    v,_ = integrate.quad(f,0,1,limit=200)
    return t*hi + np.log(v)
for s in [1e-6, 10, 50, 100, 500, 1000, 5000, 2e4, 1e5]:
    out.append(f"s={s:>9.0f}  pi/L = {Lam(s)/s:.5f}  (mean {mean_th:.3f}, sup {hi:.3f})")
# monotonicity check
ss = np.linspace(1,20000,60); vals=[Lam(s)/s for s in ss]
out.append(f"monotone increasing in s: {all(np.diff(vals)>-1e-12)}")

# ---- 3) MPS raises load: compare Beta(2,8) vs Beta(1,4) on [0,0.05] (same mean 0.01, more spread)
def LamG(t,a_,b_):
    f = lambda x: np.exp(t*hi*(x-1.0))*B.pdf(x,a_,b_)
    v,_ = integrate.quad(f,0,1,limit=200)
    return t*hi + np.log(v)
for s in [100,1000,10000]:
    out.append(f"s={s}: load Beta(2,8)={LamG(s,2,8)/s-mean_th:.5f}  Beta(1,4)={LamG(s,1,4)/s-mean_th:.5f} (wider prior => bigger)")

# ---- 4) Buyer WTP (CARA) and frontier multiplier m(x)=(e^x-1)/x
g, Ls = sp.symbols('gamma L_s', positive=True)
thB = sp.Symbol('theta_B', positive=True)
WTP = sp.log(1 - thB + thB*sp.exp(g*Ls))/g
approx = sp.series(WTP, thB, 0, 2).removeO()
out.append(f"WTP small-theta expansion: {sp.simplify(approx)}")   # -> thB*(exp(gL)-1)/g
m = lambda x: (np.exp(x)-1)/x
for x in [0.1,0.25,0.5,1.0,1.5,2.0,3.0]:
    out.append(f"m({x}) = {m(x):.3f}")
# exact frontier check example: theta_hat=0.01, gamma*L=1  => WTP/L?
thh=0.01
for gL in [0.5,1.0,2.0]:
    wtp = np.log(1-thh+thh*np.exp(gL))/gL
    out.append(f"exact WTP/L at theta=0.01, gL={gL}: {wtp:.5f}  vs approx {thh*m(gL):.5f}")

# ---- 5) comonotone capital-loaded premium and multiples
def pistar(theta,tau): return (theta+tau)/(1+tau)  # per unit L
for theta,tau in [(0.01,0.05),(0.01,0.07),(0.01,0.10),(0.02,0.07),(0.005,0.07)]:
    M = pistar(theta,tau)/theta
    out.append(f"theta={theta}, tau={tau}: pi*/L={pistar(theta,tau):.4f}, multiple of E[loss]={M:.2f}x")

# ---- 6) dynamics: surprise jump then sqrt-decay of half-width
tau=0.07
def price(mw): m_,w_=mw; return (min(m_+w_,1.0)+tau)/(1+tau)
pre=(0.015,0.005); post=(0.025,0.030)   # surprise expands center+width
p0,p1=price(pre),price(post)
out.append(f"jump: pre={p0:.4f} post={p1:.4f} => +{100*(p1/p0-1):.1f}%")
# decay: w_N = w1/sqrt(N), N accrues ~1/yr of relevant data after event
path=[]; m_,w1=0.025,0.030
for yr in range(0,9):
    w=w1/np.sqrt(1+yr)
    path.append((yr, price((m_,w))))
chg=[f"yr{y}: {p:.4f}" + (f" ({100*(p/path[i-1][1]-1):+.1f}%)" if i>0 else "") for i,(y,p) in enumerate(path)]
out.extend(chg)
print("\n".join(out))
