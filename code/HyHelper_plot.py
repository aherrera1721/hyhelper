from .HyHelper_traj import *
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = [15, 15]

"""
**NOTE** Working on functionality with a different plotter (besides matplotlib/Basemap)
since jupyter notebooks produce images (so interactive plots don't work)
"""

def get_dims(plot_objs):
    """
    Gets the appropriate dimensions for the amount of objects going to be plotted.
    Adds columns before rows.
    """
    total = len(plot_objs)
    row, col = 1, 1
    while True:
        if row * col >= total:
            break
        elif col == row:
            col += 1
        else:
            row += 1 
    return (row, col)

def get_vmin_vmax(plot_objs, var):
    """
    Gets the minimum and maximum values of the desired variable.
    """
    vmin, vmax = plot_objs[0].min_vals[var], plot_objs[0].max_vals[var]

    for plot_obj in plot_objs:
        if plot_obj.min_vals[var] < vmin:
            vmin = plot_obj.min_vals[var]
        if plot_obj.max_vals[var] > vmax:
            vmax = plot_obj.max_vals[var]

    return (vmin, vmax)
    
def make_scatter(fig, axes, traj, coords, title, ax_ind, var, norm, cmap, multi_obj):
    """
    Makes a colormapped scatterplot from the given trajectory.
    """
    if multi_obj:
        axes[ax_ind].set_title(title)
    else:
        axes.set_title(title)

    lat, lon = coords[0], coords[1]

    if multi_obj:
        bmap = Basemap(projection='cyl', llcrnrlat=lat-4, urcrnrlat=lat+4, llcrnrlon=lon-5, urcrnrlon=lon+5, resolution='l', ax=axes[ax_ind])
    else:
        bmap = Basemap(projection='cyl', llcrnrlat=lat-4, urcrnrlat=lat+4, llcrnrlon=lon-5, urcrnrlon=lon+5, resolution='l', ax=axes)
    bmap.drawmapboundary()
    bmap.drawcoastlines()
    bmap.drawcountries()

    lons = [point.lon for point in traj]
    lats = [point.lat for point in traj]
    data = [point.data[var] for point in traj]

    if multi_obj: 
        sc = bmap.scatter(lons, lats, c=data, cmap=cmap, norm=norm, alpha=0.5, ax=axes[ax_ind], latlon=True)
    else:
        sc = bmap.scatter(lons, lats, c=data, cmap=cmap, norm=norm, alpha=0.5, ax=axes, latlon=True)

def gen_plots(plot_objs, coords, var="PRESSURE", dims=None, cmap='Blues'):
    """
    Generates the plot of trajectory objects in a series of subplots with one colorbar on the right side.
    The plots are centered around the given coords.
    """
    if not isinstance(plot_objs, list):
        plot_objs = [plot_objs]
        multi_obj = False
    else:
        multi_obj = True

    if not dims:
        rows, cols = get_dims(plot_objs)

    fig, axes = plt.subplots(rows, cols)

    if multi_obj:
        axes = axes.flatten()

    ax_ind = 0
    vmin, vmax = get_vmin_vmax(plot_objs, var)
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    for plot_obj in plot_objs: ## plots each object ##
        if isinstance(plot_obj, Traj):
            title = plot_obj.traj_name
            make_scatter(fig, axes, plot_obj, coords, title, ax_ind, var, norm, cmap, multi_obj)
            ax_ind += 1
        elif isinstance(plot_obj, Traj_Group):
            title = plot_obj.group_name
            for traj in plot_obj:
                make_scatter(fig, axes, traj, coords, title, ax_ind, var, norm, cmap, multi_obj)
            ax_ind += 1

    while ax_ind < rows*cols: ## delete unused subplots ##
        fig.delaxes(axes[ax_ind])
        ax_ind += 1

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    if multi_obj:
        bar = fig.colorbar(mappable=sm, ax=axes.ravel().tolist())
    else:
        bar = fig.colorbar(mappable=sm, ax=axes)
    bar.set_label(var)
    plt.figure(figsize=(60,30))
    plt.show()
