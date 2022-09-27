import time
from dateutil.tz import tzlocal
from pandas import DataFrame
from numpy import datetime64
from pandas import DatetimeIndex
from matplotlib.dates import DateFormatter
from matplotlib.figure import Figure


figure = Figure(figsize=(7, 9))
figure.add_subplot()
ax = figure.axes[0]
now = time.time()
dt64s = [
    datetime64(int(when), 's')
    for when in (now + i * 900 for i in range(-90, 1))
]
dti = DatetimeIndex(dt64s)  ##, tz=tzlocal())
print(dti)
data = {
    'a': [i for i, _ in enumerate(dt64s)],
    'b': [i + 1 for i, _ in enumerate(dt64s)]
}
df = DataFrame(data, index=dti)  ## dt64s
dfmt = DateFormatter("%Y-%m-%d %H:%M:%S %z %Z", tz=tzlocal())
ax.xaxis.set_major_formatter(dfmt)
ax.set_title(f"Data from {dti[0]}..{dti[-1]}")
df.plot(ax=ax)
figure.savefig('plot1.png')