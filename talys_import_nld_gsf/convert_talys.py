"""
A scripy to convert nld and gsfs to a format readable by talys

Author: Fabio Zeiser, Oct 2019
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from spinfunctions import SpinFunctions


def talys_Egrid():
    ex_binning = np.zeros((6, 2)) # format: [Nbins_cum, binwidth]
    ex_binning[0, :] = [19+1, 0.25]  # 0.25 MeV from Ex=0.25 - 5.00 MeV,i=0-19
    ex_binning[1, :] = [29+1, 0.50]  # 0.50 MeV from Ex=5.50 - 10.0 MeV,i=20-29
    ex_binning[2, :] = [39+1, 1.00]  # 1.00 MeV from Ex=11.0 - 20.0 MeV,i=30-39
    ex_binning[3, :] = [41+1, 2.50]  # 2.50 MeV from Ex=22.5 - 25.0 MeV,i=40-41
    ex_binning[4, :] = [42+1, 5.00]  # 5.00 MeV from Ex=25.0 - 30.0 MeV,i=41-42
    ex_binning[5, :] = [54+1, 10.0]  # 10.0 MeV from Ex=30.0 - 150. MeV,i=43-54

    E = np.array([])
    for i in range(len(ex_binning)):
        binwidth = ex_binning[i, 1]
        if i == 0:
            N = ex_binning[0, 0]
            Estart = 0
        else:
            N = ex_binning[i, 0] - ex_binning[i-1, 0]
            Estart = E[-1]
        # print(np.arange(start=1, stop=N+1))
        E = np.append(E, np.arange(start=1, stop=N+1)*binwidth + Estart)
    return E


def log_interp1d(xx, yy, **kwargs):
    """ Interpolate a 1-D function.logarithmically """
    logy = np.log(yy)
    lin_interp = interp1d(xx, logy, kind='linear', **kwargs)
    log_interp = lambda zz: np.exp(lin_interp(zz))
    return log_interp


def gen_nld_table(fnld, Estop, model, spinpars, A):
    """ Generates talys-style table from a total nld and spin model

    Args:
        fnld (function): fnld(E) should give the total nld
            for the energy E [MeV]
        Estop (float): Result will stop at the energy in the grid just
            above `Estop`.
        model (str): Which spincut mdoel to use
        spinpars (dict): Dictionary with necessary parameters for `model`.

    Returns:
        out (ndarray): Array with columns
            [U[MeV], T[MeV], NCUMUL, RHOOBS, RHOTOT, NLD_per_J[...] ]

    Note: The temperature here is just a dummy. Also, for now
        `RHOOBS` will be set to `RHOTOT`
    """
    # prepare NLD
    E = talys_Egrid()
    iSn = np.searchsorted(E, Estop) + 1  # take right side
    E = E[:iSn+1]

    Js = np.arange(0, 30)  # 0 to stop-1
    if A % 2 == 1:
        Js + 0.5
    spindist = SpinFunctions(E, Js, model=model, pars=spinpars).distibution()
    spindist /= spindist.sum(axis=1)[:, np.newaxis]

    # fake temperature
    T_dummy = np.full_like(E, 0.5)

    nld = fnld(E)
    out = np.column_stack((E, T_dummy, np.cumsum(nld),
                           nld, nld))
    nld_per_J = nld[:, np.newaxis]*spindist
    assert(np.allclose(nld, nld_per_J.sum(axis=1))), "Must have stacked badly"
    out = np.c_[out, nld_per_J]
    return out


def sigma2(Ex, model, pars):
    """ wrapper for spincut from SpinFunctions"""
    return SpinFunctions(Ex, model=model, pars=pars).get_sigma2()


if __name__ == "__main__":
    # Constants for the spin distribution / NLD
    Sn = 6.534
    dE = 1  # extend the model used with the Oslo data a little further
    Estop = Sn+dE
    A = 240
    Z = 94
    # From EB05 for this nucleus
    spinpars = {"mass": A, "NLDa": 25.160, "Eshift": 0.120}

    # load/write nld
    fn_nld = "data/nld_new.txt"
    fn_nld_out = "data/nld_totalys.txt"
    nld = np.loadtxt(fn_nld)

    # If you comment out extrapolation below, it will do a log-linear
    # extraolation of the last two points. This is probably not what you want.
    # fnld = log_interp1d(nld[:, 0], nld[:, 1], fill_value="extrapolate")
    fnld = log_interp1d(nld[:, 0], nld[:, 1])

    # print(f"Below {nld[0, 0]} the nld is just an extrapolation
    #       "Best will be to use discrete levels in talys below that")
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

    # read/write gsf files
    fn_gsf = "data/GSFTable_py.dat"
    fn_gsf_outE1 = "data/gsfE1.dat"
    fn_gsf_outM1 = "data/gsfM1.dat"
    gsf = np.loadtxt(fn_gsf)
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


    header = f" Z=  {Z} A=  {A}\n" + "  U[MeV]  fE1[mb/MeV]"
    # gsfE1 /= factor_from_mb
    np.savetxt(fn_gsf_outE1, np.c_[Egsf_out, fE1(Egsf_out)/factor_from_mb],
               fmt="%9.3f%12.3E", header=header)
    # gsfM1 /= factor_from_mb
    np.savetxt(fn_gsf_outM1, np.c_[Egsf_out, fM1(Egsf_out)/factor_from_mb],
               fmt="%9.3f%12.3E", header=header)

    fig, ax = plt.subplots()
    ax.semilogy(Egsf_out, fE1(Egsf_out), label="E1")
    ax.semilogy(Egsf_out, fM1(Egsf_out), "--", label="M1")
    ax.axvspan(Egsf[-1], Egsf_out[-1], alpha=0.1, label="extrapolation")

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
