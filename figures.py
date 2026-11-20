"""Figures 1 to 3, written to results/ as PDF and PNG."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import beta as B
from scipy import integrate

plt.rcParams.update({
    "font.family": "serif", "font.size": 9.5, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.7, "xtick.major.width": 0.7,
    "ytick.major.width": 0.7, "figure.dpi": 200, "mathtext.fontset": "stix",
})
BLUE, VERM, GREY = "#2456A4", "#C1441E", "#666666"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=200)
    plt.close(fig)

# ---------- Fig 1: ambiguity load convergence, two priors ----------
hi = 0.05
def piL(t, a_, b_):
    if t < 1e-9: return hi*a_/(a_+b_)
    # stable log-sum-exp style: Lambda(t) = t*hi + log E exp(t*hi*(x-1))
    f = lambda x: np.exp(t*hi*(x-1.0))*B.pdf(x, a_, b_)
    v,_ = integrate.quad(f, 0, 1, limit=400)
    return (t*hi + np.log(v))/t

s = np.concatenate([np.linspace(0, 400, 200), np.linspace(400, 20000, 300)])
y1 = [piL(t, 2, 8) for t in s]     # tighter prior, mean .01
y2 = [piL(t, 1, 4) for t in s]     # wider prior,   mean .01

fig, ax = plt.subplots(figsize=(5.2, 3.1))
ax.semilogx(1+s, np.array(y1)/1, color=BLUE, lw=1.6, label=r"tighter second-order prior ($\mu_1$)")
ax.semilogx(1+s, np.array(y2)/1, color=VERM, lw=1.6, ls="--", label=r"wider second-order prior ($\mu_2$)")
ax.axhline(0.01, color=GREY, lw=0.8, ls=":")
ax.axhline(0.05, color=GREY, lw=0.8, ls=":")
ax.text(1.35, 0.0122, r"$\hat\theta L$  (mean-based, 'actuarially fair')", fontsize=8, color=GREY)
ax.text(1.35, 0.0472, r"$\bar\theta L$  (worst case in $\Theta$)", fontsize=8, color=GREY)
ax.set_xlabel(r"book scale $s=\eta n L$  (log scale)")
ax.set_ylabel(r"reservation premium $\pi_n$ (per unit $L$)")
ax.set_ylim(0.005, 0.055)
ax.legend(frameon=False, fontsize=8, loc="lower right", bbox_to_anchor=(0.98, 0.12))
fig.tight_layout(); save(fig, "fig1_load")

# ---------- Fig 2: insurability frontier ----------
x = np.linspace(0.05, 3.2, 400)
m = (np.exp(x)-1)/x
fig, ax = plt.subplots(figsize=(5.2, 3.3))
ax.plot(x, m, color=BLUE, lw=1.8)
ax.fill_between(x, 1, m, color=BLUE, alpha=0.10)
ax.set_ylim(1, 8); ax.set_xlim(0, 3.2)
ax.text(2.05, 2.1, "insurable:\ntrade survives worst-case pricing", fontsize=8.5, color=BLUE)
ax.text(0.28, 5.6, "uninsurable:\nambiguity ratio exceeds\nrisk-aversion multiplier", fontsize=8.5, color=VERM)
# illustrative peril placements
perils = [ (1.6, 1.5, "residential windstorm\n(modelled)"),
           (1.0, 2.6, "cyber, single-firm"),
           (0.55, 4.8, "cyber, systemic"),
           (0.35, 6.8, "pandemic BI") ]
for (px, py, lab) in perils:
    ax.plot(px, py, marker="o", ms=4.5, color=VERM if py > (np.exp(px)-1)/px else BLUE)
    ax.annotate(lab, (px, py), textcoords="offset points", xytext=(7, -2), fontsize=7.5)
ax.set_xlabel(r"buyer stake $\times$ risk aversion, $\gamma L$")
ax.set_ylabel(r"ambiguity ratio $a=\bar\theta/\hat\theta$")
fig.tight_layout(); save(fig, "fig2_frontier")

# ---------- Fig 3: price path after a model surprise ----------
tau = 0.07
def price(m_, w_): return (min(m_+w_, 1.0)+tau)/(1+tau)
T = np.arange(-3, 10)
m0, w0 = 0.015, 0.005
m1, w1 = 0.025, 0.030
p = []
for t in T:
    if t < 0: p.append(price(m0, w0))
    else:     p.append(price(m1, w1/np.sqrt(1+t)))
p = np.array(p)/price(m0,w0)*100
fig, ax = plt.subplots(figsize=(5.2, 3.0))
ax.step(T, p, where="post", color=BLUE, lw=1.7)
ax.axvline(0, color=VERM, lw=0.9, ls="--")
ax.text(-2.9, 133.5, "model surprise:\nconventional set expands,\n$(m,w)$ jump", fontsize=8, color=VERM)
ax.text(2.9, 104.5, "confirming data arrive at rate $\\propto\\hat\\theta$:\n$w_t=w_1/\\sqrt{1+t}$, slow softening", fontsize=8, color=GREY)
ax.set_xlabel("years relative to surprise event")
ax.set_ylabel("premium index (pre-event = 100)")
ax.set_ylim(95, 145)
fig.tight_layout(); save(fig, "fig3_path")
print("figures written to results/: fig1_load, fig2_frontier, fig3_path (PDF and PNG)")
