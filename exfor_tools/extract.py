import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

names = ["x", "dx", "y", "dy", "#1",
         "year, auth", "#2", "id", "com"]
data = pd.read_fwf("X4_exp.txt", skiprows=11, skipfooter=2, names=names)
data.drop(columns=["#1", "#2"])


df = data.groupby("year, auth")
fig, ax = plt.subplots()

outdir = "split"
os.mkdir(outdir)

for name, group in df:
    ax.errorbar(group["x"], group["y"], yerr=group["dy"], label=name, fmt="o",
                alpha=0.5, markerfacecolor="None")
    outname = name.replace(" ", "_")
    group.to_csv(f"{outdir}/{outname}", sep="\t")

ax.set_yscale("log")
ax.set_xlim(0, 20)
ax.set_ylim(1e0, 1e2)
ax.legend()

plt.show()
