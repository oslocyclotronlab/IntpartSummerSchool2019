"""
Convert the nld table with the total nld to
the TALYS readable format
"""
import numpy as np
import matplotlib.pyplot as plt
import sys
sys.path.append("../../../talys_import_nld_gsf")
from convert_talys import gen_nld_table, sigma2, log_interp1d

def CT(E, T, E0):
    return np.c_[E, np.exp((E-E0)/T)/T]

# Constants for the spin distribution / NLD
Sn = 7.558
En = 2  # extend the model used with the Oslo data a little further
Estop = Sn+En
A = 192
Z = 76
# From mixture between discretes and EB05 for this nucleus
model = "Disc_and_EB05"
spinpars = {"mass": A, "NLDa": 18.472, "Eshift": 0.331,
            "sigma2_disc": [1.1, 2.8], "Sn": Sn}

# load/write nld
fn_nld = "../nld_exp.txt"
fn_nld_out = "data/nld_talys.txt"
nld = np.loadtxt(fn_nld, usecols=[0,1])
nld_exp = nld.copy()

# Add the same extrapolation
Emax = nld[-1, 0]
x = np.linspace(Emax, Estop+3, 50)
nld_ext = CT(x, T=0.5, E0=0.311)
nld = np.append(nld, nld_ext, axis=0)

# If you comment out extrapolation below, it will do a log-linear
# extraolation of the last two points. This is probably not what you want.
# fnld = log_interp1d(nld[:, 0], nld[:, 1], fill_value="extrapolate")
fnld = log_interp1d(nld[:, 0], nld[:, 1])

try:
    table = gen_nld_table(fnld=fnld, Estop=Estop, model="EB05",
                          spinpars=spinpars, A=A)
except ValueError as e:
    print(str(e))
    if str(e) == "A value in x_new is below the interpolation range.":
        raise ValueError("The last values in the data are below "
                         f"Estop={Estop} if you really want to get "
                         "the data in talys format so far you need to"
                         "use an extrapolation.")
        raise
    else:
        raise

fmt = "%7.2f %6.3f %9.2E %8.2E %8.2E " + 30*" %8.2E"
header = "U[MeV]  T[MeV]  NCUMUL   RHOOBS   RHOTOT     J=0      J=1      J=2      J=3      J=4      J=5      J=6      J=7      J=8      J=9     J=10     J=11     J=12     J=13     J=14     J=15     J=16     J=17     J=18     J=19     J=20     J=21     J=22     J=23     J=24     J=25     J=26     J=27     J=28     J=29"
np.savetxt(fn_nld_out, table, fmt=fmt, header=header)

print("Rembember to  overwrite part of the table in"
      "`path/to/talys/structure/density/ground/goriely/XX.tab` with the"
      f"generated nld file: {fn_nld_out}")

fig, ax = plt.subplots()
ax.semilogy(nld_exp[:, 0], nld_exp[:, 1], "o", label="nld tot, input")
ax.semilogy(nld_ext[:, 0], nld_ext[:, 1], "o", label="nld tot, extrapolation")
ax.semilogy(table[:, 0], table[:, 4], label="nld tot_out")
ax.set_xlabel("Ex [MeV]")
ax.set_ylabel("NLD [1/MeV]")
ax.legend()

fig, ax = plt.subplots()
ax.plot(nld[:, 0], np.sqrt(sigma2(nld[:, 0], model, spinpars)),
        label="nld tot")
ax.set_xlabel("Ex [MeV]")
ax.set_ylabel(r"spincut $\sigma$")


plt.show()
# ax.semilogy(Egsf_out, fM1(Egsf_out), "--", label="M1")

# # read/write gsf files
# fn_gsf = "data/GSFTable_py.dat"
# fn_gsf_outE1 = "data/gsfE1.dat"
# fn_gsf_outM1 = "data/gsfM1.dat"
# gsf = np.loadtxt(fn_gsf)
# # The file is/should be writen in [MeV] [MeV^-3] [MeV^-3]
# if gsf[0, 0] == 0:
#     gsf = gsf[1:, :]
# Egsf = gsf[:, 0]
# gsfE1 = gsf[:, 1]
# gsfM1 = gsf[:, 2]

# # REMEMBER that the TALYS functions are given in mb/MeV (Goriely's tables)
# # so we must convert it (simple factor)
# factor_from_mb = 8.6737E-08   # const. factor in mb^(-1) MeV^(-2)

# fE1 = log_interp1d(Egsf, gsfE1, fill_value="extrapolate")
# fM1 = log_interp1d(Egsf, gsfM1, fill_value="extrapolate")

# Egsf_out = np.arange(0.1, 30.1, 0.1)


# header = f" Z=  {Z} A=  {A}\n" + "  U[MeV]  fE1[mb/MeV]"
# # gsfE1 /= factor_from_mb
# np.savetxt(fn_gsf_outE1, np.c_[Egsf_out, fE1(Egsf_out)/factor_from_mb],
#            fmt="%9.3f%12.3E", header=header)
# # gsfM1 /= factor_from_mb
# np.savetxt(fn_gsf_outM1, np.c_[Egsf_out, fM1(Egsf_out)/factor_from_mb],
#            fmt="%9.3f%12.3E", header=header)

# fig, ax = plt.subplots()
# ax.semilogy(Egsf_out, fE1(Egsf_out), label="E1")
# ax.semilogy(Egsf_out, fM1(Egsf_out), "--", label="M1")

# try:
#     talys_out = np.loadtxt("data/talys_output.txt", skiprows=2)
#     ax.plot(talys_out[:, 0], talys_out[:, 1], "-.",
#             label="talys_output M1")
#     ax.plot(talys_out[:, 0], talys_out[:, 2], "--",
#             label="talys_output E1")
# except OSError:
#     pass
# ax.legend()
# plt.show()
