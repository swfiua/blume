import matplotlib.pyplot as plt
import numpy as np
from matplotlib.testing.decorators import image_comparison
from matplotlib.colors import Normalize

from blume.table import Cell, Table, table
from matplotlib.path import Path


def test_non_square():
    # Check that creating a non-square table works
    cellcolors = ['b', 'r']
    plt.table(cellColours=cellcolors)


@image_comparison(['table_zorder.png'], remove_text=True,
                  checksums=['e057420d1d4440fb33c9d25b312f8878'])
def test_zorder():
    data = [[66386, 174296],
            [58230, 381139]]

    colLabels = ('Freeze', 'Wind')
    rowLabels = ['%d year' % x for x in (100, 50)]

    cellText = []
    yoff = np.zeros(len(colLabels))
    for row in reversed(data):
        yoff += row
        cellText.append(['%1.1f' % (x/1000.0) for x in yoff])

    t = np.linspace(0, 2*np.pi, 100)
    plt.plot(t, np.cos(t), lw=4, zorder=2)

    table(plt.gca(),
        cellText=cellText,
        rowLabels=rowLabels,
        colLabels=colLabels,
        loc='center',
        zorder=-2)

    table(plt.gca(),
        cellText=cellText,
        rowLabels=rowLabels,
        colLabels=colLabels,
        loc='upper center',
        zorder=4)
    
    plt.yticks([])


@image_comparison(['table_labels.png'],
                  checksums=['8e973562586d435317e7a57bc3f6f91e'])
def test_label_colours():
    dim = 3

    c = np.linspace(0, 1, dim)
    colours = plt.cm.RdYlGn(c)
    cellText = [['1'] * dim] * dim

    fig = plt.figure()

    ax1 = fig.add_subplot(4, 1, 1)
    ax1.axis('off')
    table(
        ax1,
        cellText=cellText,
        rowColours=colours,
        loc='best')

    ax2 = fig.add_subplot(4, 1, 2)
    ax2.axis('off')
    table(
        ax2,
        cellText=cellText,
        rowColours=colours,
        rowLabels=['Header'] * dim,
        loc='best')

    ax3 = fig.add_subplot(4, 1, 3)
    ax3.axis('off')
    table(
        ax3,
        cellText=cellText,
        colColours=colours,
        loc='best')

    ax4 = fig.add_subplot(4, 1, 4)
    ax4.axis('off')
    table(
        ax4,
        cellText=cellText,
        colColours=colours,
        colLabels=['Header'] * dim,
        loc='best')


@image_comparison(['table_cell_manipulation.png'], remove_text=True,
                  checksums=['3b6462922fa1402c7da77bc7af4c12f7'])
def test_diff_cell_table():
    cells = ('horizontal', 'vertical', 'open', 'closed', 'T', 'R', 'B', 'L')
    cellText = [['1'] * len(cells)] * 2
    colWidths = [0.1] * len(cells)

    _, axs = plt.subplots(nrows=len(cells), figsize=(4, len(cells)+1))
    for ax, cell in zip(axs, cells):
        table(ax,
              colWidths=colWidths,
              cellText=cellText,
              loc='center',
              edges=cell)
        ax.axis('off')
    plt.tight_layout()


def test_cell_visible_edges():
    types = ('horizontal', 'vertical', 'open', 'closed', 'T', 'R', 'B', 'L')
    codes = (
        (Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO, Path.MOVETO),
        (Path.MOVETO, Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO),
        (Path.MOVETO, Path.MOVETO, Path.MOVETO, Path.MOVETO, Path.MOVETO),
        (Path.MOVETO, Path.LINETO, Path.LINETO, Path.LINETO, Path.CLOSEPOLY),
        (Path.MOVETO, Path.MOVETO, Path.MOVETO, Path.LINETO, Path.MOVETO),
        (Path.MOVETO, Path.MOVETO, Path.LINETO, Path.MOVETO, Path.MOVETO),
        (Path.MOVETO, Path.LINETO, Path.MOVETO, Path.MOVETO, Path.MOVETO),
        (Path.MOVETO, Path.MOVETO, Path.MOVETO, Path.MOVETO, Path.LINETO),
        )

    for t, c in zip(types, codes):
        cell = Cell((0, 0), visible_edges=t, width=1, height=1)
        code = tuple(s for _, s in cell.get_path().iter_segments())
        assert c == code


@image_comparison(['table_auto_column.png'],
                  checksums=['09f6c7399bb0d20478c30104e61fe572'])
def test_auto_column():
    fig = plt.figure()

    # iterable list input
    ax1 = fig.add_subplot(4, 1, 1)
    ax1.axis('off')
    tb1 = table(ax1,
        cellText=[['Fit Text', 2],
                  ['very long long text, Longer text than default', 1]],
        rowLabels=["A", "B"],
        colLabels=["Col1", "Col2"],
        loc="center")
    tb1.auto_set_font_size(False)
    tb1.set_fontsize(12)
    tb1.auto_set_column_width([-1, 0, 1])

    # iterable tuple input
    ax2 = fig.add_subplot(4, 1, 2)
    ax2.axis('off')
    tb2 = table(ax2,
        cellText=[['Fit Text', 2],
                  ['very long long text, Longer text than default', 1]],
        rowLabels=["A", "B"],
        colLabels=["Col1", "Col2"],
        loc="center")
    tb2.auto_set_font_size(False)
    tb2.set_fontsize(12)
    tb2.auto_set_column_width((-1, 0, 1))

    # 3 single inputs
    ax3 = fig.add_subplot(4, 1, 3)
    ax3.axis('off')
    tb3 = table(ax3,
        cellText=[['Fit Text', 2],
                  ['very long long text, Longer text than default', 1]],
        rowLabels=["A", "B"],
        colLabels=["Col1", "Col2"],
        loc="center")
    tb3.auto_set_font_size(False)
    tb3.set_fontsize(12)
    tb3.auto_set_column_width(-1)
    tb3.auto_set_column_width(0)
    tb3.auto_set_column_width(1)

    # 4 non integer iterable input
    ax4 = fig.add_subplot(4, 1, 4)
    ax4.axis('off')
    tb4 = table(ax4,
        cellText=[['Fit Text', 2],
                  ['very long long text, Longer text than default', 1]],
        rowLabels=["A", "B"],
        colLabels=["Col1", "Col2"],
        loc="center")
    tb4.auto_set_font_size(False)
    tb4.set_fontsize(12)
    tb4.auto_set_column_width("-101")


@image_comparison(['table_bbox.png'],
                  checksums=['faaebec0768be7c877d0cb742553c3b9'])
def test_bbox_table():

    fig = plt.figure()

    data = [
        [1, 10, 100],
        [2, 40,  50],
        [1, 10,  80],
        [4, 20,  60]]

    norm = Normalize()
    colours = plt.cm.RdYlGn(norm(data))

    alpha = 0.2
    colours[:, :, 3] = alpha
    ax = fig.add_subplot(1, 1, 1)
    ax.axis('off')

    table(ax,
        cellText=data,
        cellColours=colours,
        bbox=(.0, .0, 1, 1))

    plt.draw()


@image_comparison(['table_bad_pad.png'],
                  checksums=['fff8eea1f2c0214d6a4d37fcfc5cd24d'])
def test_bad_pad_table():

    size_x, size_y = 12, 4
    fig = plt.figure(figsize=(size_x, size_y))
    ax = fig.add_subplot(111)

    cellText = list(zip(*[
        ["R001", "R002", "R003", "R005", "R006", "R007"],
        [50*"*", 10*"-", 70*"x", "R005", "R006", "R007"],
        [3,       1,      3,      4,      2,      3],
        [4,       2,      3,      2,      4,      3],
        [12,      2,      9,      8,      8,      9]]))

    colLabels = ["ID", "Title", "X-Pos", "Y-Pos", "Value"]

    rowLabels = list(range(len(cellText)))

    # Left aligned cell text uses weird spacing
    # (if txt is long)
    the_table = table(plt.gca(),
        cellText=cellText, rowLabels=rowLabels, colLabels=colLabels,
        loc='upper center', cellLoc="left",
        colWidths=[0.05, 0.52, 0.05, 0.05, 0.05, 0.05])

    the_table.auto_set_font_size(False)
    the_table.set_fontsize(8)

    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plt.draw()


def test_table_cells():
    fig, ax = plt.subplots()
    table = Table(ax)

    cell = table.add_cell(1, 2, 1, 1)
    assert isinstance(cell, Cell)
    assert cell is table[1, 2]

    cell2 = Cell((0, 0), 1, 2, visible_edges=None)
    table[2, 1] = cell2
    assert table[2, 1] is cell2

    # make sure gettitem support has not broken
    # properties and setp
    table.properties()
    plt.setp(table)
