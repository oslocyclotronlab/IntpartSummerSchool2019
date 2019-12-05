import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../../talys_import_nld_gsf")
from convert_talys import gen_nld_table, sigma2, log_interp1d

# commonly used const. strength_factor, convert in mb^(-1) MeV^(-2)
strength_factor = 8.6737E-08


def SLO(E, E0, Gamma0, sigma0):
    # Special Lorentzian,
    # adapted from Kopecky & Uhl (1989) eq. (2.1)
    f = strength_factor * sigma0 * E * Gamma0**2 / \
        ((E**2 - E0**2)**2 + E**2 * Gamma0**2)
    return f


def GLO(E, E0, Gamma0, sigma0, T):
    # Generalized Lorentzian,
    # adapted from Kopecky & Uhl (1989) eq. (2.3-2.4)
    Gamma = Gamma0 * (E**2 + 4 * np.pi**2 * T**2) / E0**2
    f1 = (E * Gamma) / ((E**2 - E0**2)**2 + E**2 * Gamma**2)
    f2 = 0.7 * Gamma0 * 4 * np.pi**2 * T**2 / E0**5

    f = strength_factor * sigma0 * Gamma0 * (f1 + f2)
    return f


# Constants
Sn = 7.558
A = 192
Z = 76

# parameters
pGLO = {"E0": 13.2, "Gamma0": 2.8, "sigma0": 615, "T": 1.2 }
pSLO = {"E0": 7.1, "Gamma0": 4, "sigma0": 2.1}

# For this exercise we don't read the data from file,
# but create an equivalent type of array
# gsf = np.loadtxt(fn_gsf)
x = np.linspace(0, Sn+20)
gsf = np.zeros((len(x), 3))
gsf[:, 0] = x
gsf[:, 1] = GLO(x, **pGLO)
gsf[:, 2] = SLO(x, **pSLO)

# The file is/should be writen in [MeV] [MeV^-3] [MeV^-3]
if gsf[0, 0] == 0:
    gsf = gsf[1:, :]
Egsf = gsf[:, 0]
gsfE1 = gsf[:, 1]
gsfM1 = gsf[:, 2]

# REMEMBER that the TALYS functions are given in mb/MeV (Goriely's tables)
# so we must convert it (simple factor)
factor_from_mb = 8.6737E-08   # const. factor in mb^(-1) MeV^(-2)

fE1 = log_interp1d(Egsf, gsfE1, fill_value="extrapolate")
fM1 = log_interp1d(Egsf, gsfM1, fill_value="extrapolate")

Egsf_out = np.arange(0.1, 30.1, 0.1)

fn_gsf_outE1 = "data/gsfE1.dat"
fn_gsf_outM1 = "data/gsfM1.dat"
header = f" Z=  {Z} A=  {A}\n" + "  U[MeV]  fE1[mb/MeV]"
# gsfE1 /= factor_from_mb
np.savetxt(fn_gsf_outE1, np.c_[Egsf_out, fE1(Egsf_out)/factor_from_mb],
           fmt="%9.3f%12.3E", header=header)
# gsfM1 /= factor_from_mb
np.savetxt(fn_gsf_outM1, np.c_[Egsf_out, fM1(Egsf_out)/factor_from_mb],
           fmt="%9.3f%12.3E", header=header)

fig, ax = plt.subplots()
ax.semilogy(Egsf_out, fE1(Egsf_out), "--", label="E1")
ax.semilogy(Egsf_out, fM1(Egsf_out), "--", label="M1")
ax.semilogy(Egsf_out, fE1(Egsf_out)+fM1(Egsf_out),
            "-", label="sum")
ax.axvspan(Egsf[-1], Egsf_out[-1], alpha=0.1, label="extrapolation")

# plot together with the output from talys if existent
try:
    talys_out = np.loadtxt("data/talys_output.txt", skiprows=2)
    ax.plot(talys_out[:, 0], talys_out[:, 1], "-.",
            label="talys_output M1")
    ax.plot(talys_out[:, 0], talys_out[:, 2], "--",
            label="talys_output E1")
except OSError:
    pass
ax.legend()
plt.show()
