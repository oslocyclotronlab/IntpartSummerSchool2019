import matplotlib.pyplot as plt
import numpy as np
import itertools
import pandas as pd
import os

widths = np.array([0, 15, 28, 41, 54, 57, 82, 85, 95, 104])
widths = np.diff(widths)
names = ["x", "dx", "y", "dy", "#1",
         "year, auth", "#2", "id", "com"]
data = pd.read_fwf("X4_exp.txt", width=widths,
                   skiprows=11, skipfooter=2, names=names)
data.drop(columns=["#1", "#2"])

df = data.groupby("year, auth")

outdir = "split"
try:
    os.mkdir(outdir)
except FileExistsError:
    pass

nfigs = int(np.ceil(len(df)/5))
fig, axes = plt.subplots(nfigs, 1)
marker = itertools.cycle(('>', '+', '<', 'o', '*'))
for i, (name, group) in enumerate(df):
    ax = axes[i % nfigs] if nfigs > 0 else axes
    ax.errorbar(group["x"], group["y"], yerr=group["dy"], label=name, fmt="o",
                alpha=0.5, markerfacecolor="None",
                markersize=2, marker=next(marker))
    outname = name.replace(" ", "_")
    group.to_csv(f"{outdir}/{outname}", sep="\t")


    ax.set_yscale("log")
    ax.set_xlim(0, 20)
    ax.set_ylim(1e0, 1e2)
    ax.legend()

plt.show()
