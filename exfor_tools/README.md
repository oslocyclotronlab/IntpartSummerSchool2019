# Retriev data from EXFOR

This is a small example on how to easily extract data from EXFOR. First, select one or several dataset and plot them via `quickplot` and `receveive`. The screenshot below shows how the data files can be obtained:

![](how_to_get_data_files.png)

You can now easily read this data, see `extract.py` script.

## Code Structure:

Read the data to a `pd.Dataframe`

``` py
data = read_exfor("X4_exp.txt")
```

Now you can treat the data however you want. Eg. you plot each dataset on a common figure. In addition,
I write out each dataset as a new textfile:

``` py
df = data.groupby("year, auth")
fig, ax = plt.subplots()

for name, group in df:
    ax.errorbar(group["x"], group["y"], yerr=group["dy"], label=name, fmt="o",
                alpha=0.5, markerfacecolor="None")
    outname = name.replace(" ", "_")
    group.to_csv(f"split/{outname}", sep="\t")
```
