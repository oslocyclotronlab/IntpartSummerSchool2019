"""
primitive plotting for ex2
"""

import numpy as np
import matplotlib.pyplot as plt

xs = {}
xs["n,g"] = np.loadtxt("ex2/rp082209.tot")
xs["n,n"] = np.loadtxt("ex2/rp082208.tot")
xs["n,2n"] = np.loadtxt("ex2/rp082207.tot")

exp = {}
exp["n,g"] = np.loadtxt("ng.exp")

fig, ax = plt.subplots()

ax.plot(xs["n,g"][:, 0], xs["n,g"][:, 1], label="n,g")
ax.errorbar(exp["n,g"][:, 0], exp["n,g"][:, 1],
            yerr=exp["n,g"][:, 2], fmt="o", label="exp")

ax.set_xlabel("Energy [MeV]")
ax.set_ylabel("Cross section [mb]")
ax.legend()

ax.set_yscale("log")
ax.set_xlim(0, 20)

plt.show()
