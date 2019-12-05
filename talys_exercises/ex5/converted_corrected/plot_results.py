"""
primitive plotting for ex5
"""

import numpy as np
import matplotlib.pyplot as plt

xs = {}
xs["n,g"] = np.loadtxt("talys/rp076192.tot")
xs["n,g_ENDF"] = np.loadtxt("database/endf.dat", usecols=[0,1])
xs["macs"] = np.loadtxt("talys_astro/astrorate.g")
# xs["n,n"] = np.loadtxt("ex2/rp076192.tot")

# exp = {}
# exp["n,g"] = np.loadtxt("ng.exp")

fig, ax = plt.subplots()
ax.plot(xs["n,g"][:, 0], xs["n,g"][:, 1], label="oslo-method nld & gsf")
ax.plot(xs["n,g_ENDF"][:, 0]/1e6, xs["n,g_ENDF"][:, 1]*1000, label="ENDF/B-VIII.0")
# ax.errorbar(exp["n,g"][:, 0], exp["n,g"][:, 1],
#             yerr=exp["n,g"][:, 2], fmt="o", label="exp")

ax.set_xlabel("Energy [MeV]")
ax.set_ylabel("Cross section [mb]")
ax.legend()

ax.set_yscale("log")
ax.set_xlim(0, 0.1)
ax.set_ylim(5, 5e4)

fig, ax = plt.subplots()
ax.plot(xs["macs"][:, 0], xs["macs"][:, 2], "o-",
        label="oslo-method nld & gsf")
ax.errorbar(0.03, 2190, yerr=280, fmt="o", label="KADONIS v0.0 @30keV")
# ax.errorbar(exp["n,g"][:, 0], exp["n,g"][:, 1],
#             yerr=exp["n,g"][:, 2], fmt="o", label="exp")

ax.set_xlabel("Energy [MeV]")
ax.set_ylabel("MACS [mb]")
ax.legend()

ax.set_yscale("log")
ax.set_xlim(0, 0.1)
ax.set_ylim(200, 4000)

plt.show()
