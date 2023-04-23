import pandas as pd
import matplotlib.pyplot as plt
from blume.table import table

size_x, size_y = 12, 4
fig = plt.figure (figsize=(size_x, size_y))
ax  = fig.add_subplot(111)

col_ID    = pd.Series ([ "R001", "R002", "R003", "R005", "R006", "R007" ])
col_Title = pd.Series ([ 50*"*", 10*"-", 70*"x", "R005", "R006", "R007" ])
col_x     = pd.Series ([  3,      1,      3,      4,      2,      3 ])
col_y     = pd.Series ([  4,      2,      3,      2,      4,      3 ])

legend_df = pd.DataFrame ({ "ID"    : col_ID,
                            "Title" : col_Title,
                            "X-Pos" : col_x,
                            "Y-Pos" : col_y,
                            "Value" : col_x * col_y })
rowLabels = legend_df.index
colLabels = legend_df.columns
cellText  = legend_df.values

# Center-Aligned text looks ok
#the_table = table (ax, cellText=cellText, rowLabels=rowLabels, colLabels=colLabels, loc='upper center', cellLoc="center", colWidths=[0.05, 0.52, 0.05, 0.05, 0.05, 0.05])

# Bogus: Same colWidths, but left OR right aligned -> unwanted space in title column
the_table = table(ax, cellText=cellText, rowLabels=rowLabels, colLabels=colLabels, loc='upper center', cellLoc="left", colWidths=[0.05, 0.52, 0.05, 0.05, 0.05, 0.05])

the_table.auto_set_font_size(False)
the_table.set_fontsize (8)

ax.xaxis.set_visible (False)                                            # Grafik-Achsen ausschalten, wir wollen nur Plot
ax.yaxis.set_visible (False)
# the_table.scale(2, 2)

plt.show()
