"""
Plot rainfall data of multiple stations with colored, semi-transparent overlay


"""

# %%
fname = r"../DATA\KNMI_daggeg_2017-2019.txt "

# Zoek headerregel met kolomnamen
with open(fname) as f:
    for i, line in enumerate(f):
        if line.startswith("# STN,YYYYMMDD"):
            header_line = i
            break

# Lees data vanaf de regel na de header
df = pd.read_csv(
    fname,
    skiprows=header_line,
    # comment="#",
)

# Kolomnamen opschonen
df.columns = df.columns.str.strip()

# Datum parsen
df["YYYYMMDD"] = pd.to_datetime(df["YYYYMMDD"], format="%Y%m%d")

# Optioneel: index zetten
df = df.set_index("YYYYMMDD")

for col in ["TG", "TN", "TX"]:
    df[col] = df[col] / 10.0  # °C

df["RH"] = df["RH"].clip(lower=0) / 10 # mm, handling -1 < 0.05 mm by turning into zero

df.pivot_table(
    index=df.index,
    columns="# STN",
    values="RH",
).plot()

print(df.head())

# %%
import matplotlib.pyplot as plt

# Example structure:
# datetime index | 380 | 377 | 391 | 375 | 370 | 350 | 356

df.index = pd.to_datetime(df.index)

fig, ax = plt.subplots(figsize=(14, 5))

colours = plt.cm.tab10.colors

for i, station in enumerate(df.columns):
    ax.bar(
        df.index,
        df[station],
        width=0.8,           # suitable for daily data
        color=colours[i % len(colours)],
        alpha=0.35,
        label=str(station),
    )

ax.set(
    xlabel="Date",
    ylabel="Rainfall [mm]",
    title="Rainfall per station",
)

ax.legend(title="Station", ncols=2)
fig.autofmt_xdate()
fig.tight_layout()

plt.show()
# %%
import matplotlib.pyplot as plt

rainfall_w = df.pivot_table(
    index=df.index,
    columns="# STN",
    values="RH",
).resample("W").sum()


fig, ax = plt.subplots(figsize=(14, 5))

for station in rainfall_w.columns:
    ax.bar(
        rainfall_w.index,
        rainfall_w[station],
        alpha=0.2,
        label=station,
        width=6
    )

ax.set_xlabel("Time")
ax.set_ylabel("Rainfall [mm]")
ax.set_title("Weekly summed rainfall per station (mm)")
ax.legend(title="Station")
fig.tight_layout()

plt.show()
# %%
