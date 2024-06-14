import matplotlib.pyplot as plt
import numpy as np

from matplotlib.path import Path
import matplotlib.patches as patches

from operator import sub
def get_aspect(ax):
    # Total figure size
    figW, figH = ax.get_figure().get_size_inches()
    # Axis size on figure
    _, _, w, h = ax.get_position().bounds
    # Ratio of display units
    disp_ratio = (figH * h) / (figW * w)
    # Ratio of data units
    # Negative over negative because of the order of subtraction
    data_ratio = sub(*ax.get_ylim()) / sub(*ax.get_xlim())

    return disp_ratio / data_ratio

def draw_phase(phase, fig=None, ax=None, show=False, r=1, x0=0, y0=0,
               moon_kwargs=dict(lw=0, facecolor="wheat", clip_on=False)):

    y_scaling = 1 / get_aspect(ax)

    rad = np.pi/180
    f = np.cos(phase * rad)
    compare_func = (lambda i: np.cos(i * rad) > 0) if phase <= 180 else (lambda i: np.cos(i * rad) < 0)

    x = (f if phase <= 180 else 1) * r * np.cos(0)
    y = r * np.sin(0)

    verts = [(x + x0, y * y_scaling + y0)]
    codes = [Path.MOVETO]

    for i in range(0, 360):
        x = (f if compare_func(i) else 1) * r * np.cos(i * rad)
        y = r * np.sin(i * rad)

        verts.append((x + x0, y * y_scaling + y0))
        codes.append(Path.LINETO)
            
    verts.append(verts[0])
    codes.append(Path.CLOSEPOLY)

    path = Path(verts, codes)
    patch = patches.PathPatch(path, **moon_kwargs)

    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    ax.add_patch(patch)

    if show:
        plt.show()

    return fig, ax
