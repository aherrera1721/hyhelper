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

def choose_color(old_color=None):
    if old_color == None: return 'blue'
    color_seq = {
        'firebrick' : 'red',
        'red' : 'sandybrown', 
        'sandybrown' : 'gold',
        'gold' : 'olivedrab',
        'olivedrab' : 'mediumspringgreen',
        'mediumspringgreen' : 'lightseagreen',
        'lightseagreen' : 'deepskyblue',
        'deepskyblue' : 'blue',
        'blue' : 'mediumpurple',
        'mediumpurple' : 'plum',
        'plum' : 'mediumvioletred'
    }
    return color_seq[old_color]

def make_scatter(fig, axes, traj, coords, title, ax_ind, var, norm, cmap, multi_plot, color, label, scatter):
    """
    Makes a colormapped scatterplot from the given trajectory.
    """
    if multi_plot:
        axes[ax_ind].set_title(title)
    else:
        axes.set_title(title)

    lat, lon = coords[0], coords[1]

    if multi_plot:
        bmap = Basemap(projection='cyl', llcrnrlat=lat-4, urcrnrlat=lat+4, llcrnrlon=lon-5, urcrnrlon=lon+5, resolution='l', ax=axes[ax_ind])
    else:
        bmap = Basemap(projection='cyl', llcrnrlat=lat-4, urcrnrlat=lat+4, llcrnrlon=lon-5, urcrnrlon=lon+5, resolution='l', ax=axes)
    bmap.drawmapboundary()
    bmap.drawcoastlines()
    bmap.drawcountries()

    scatter_lons, scatter_lats, scatter_data = [], [], []
    all_lons, all_lats, all_data = [], [], []
    for point in traj:
        if point.data[var] != 0:
            scatter_lons.append(point.lon)
            scatter_lats.append(point.lat)
            scatter_data.append(point.data[var])
        all_lons.append(point.lon)
        all_lats.append(point.lat)
        all_data.append(point.data[var])

    if multi_plot:
        if scatter:
            sc = bmap.scatter(scatter_lons, scatter_lats, c=scatter_data, cmap=cmap, norm=norm, alpha=.5, ax=axes[ax_ind], latlon=True)
        l = bmap.plot(all_lons, all_lats, ax=axes[ax_ind], color=color, alpha=.75, label=label)
    else:
        if scatter:
            sc = bmap.scatter(scatter_lons, scatter_lats, c=scatter_data, cmap=cmap, norm=norm, alpha=.5, ax=axes, latlon=True)
        l = bmap.plot(all_lons, all_lats, ax=axes, color=color, alpha=.75, label=label)
    
    return l

def gen_plots(plot_objs, coords, var="PRESSURE", dims=None, cmap='Blues', scale="Lin", suptitle=None, multi_plot=True, scatter=True):
    """
    Generates the plot of trajectory objects in a series of subplots with one colorbar on the right side.
    The plots are centered around the given coords. Can set multi_plot to False if you would like to see all of your objects plotted on one plot.
    """
    if not isinstance(plot_objs, list):
        plot_objs = [plot_objs]
        multi_plot = False

    if multi_plot == False:
        rows, cols = 1, 1
    elif not dims:
        rows, cols = get_dims(plot_objs)
    else:
        rows, cols = dims

    fig, axes = plt.subplots(rows, cols)

    if suptitle != None:
        fig.suptitle(suptitle)

    if multi_plot:
        axes = axes.flatten()

    ax_ind = 0
    vmin, vmax = get_vmin_vmax(plot_objs, var)

    if scale == "Log":
        norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
    else:
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    color = None
    lines = []; labels = []
    for plot_obj in plot_objs: ## plots each object ##
        if multi_plot:
            color = 'grey'
        else:
            color = choose_color(color)

        if isinstance(plot_obj, Traj):
            if multi_plot:
                title = plot_obj.traj_name
            else:
                title = ' '

            label = plot_obj.traj_name
            l, = make_scatter(fig, axes, plot_obj, coords, title, ax_ind, var, norm, cmap, multi_plot, color, label, scatter)
            lines.append(l)
            labels.append(label)
            if multi_plot:
                ax_ind += 1
        
        elif isinstance(plot_obj, Traj_Group):
            if multi_plot:
                title = plot_obj.group_name
            else:
                title = ' '
            
            label = plot_obj.group_name
            for traj in plot_obj:
                l, = make_scatter(fig, axes, traj, coords, title, ax_ind, var, norm, cmap, multi_plot, color, label, scatter)
            lines.append(l)
            labels.append(label)
            if multi_plot:
                ax_ind += 1

    if multi_plot:
        while ax_ind < rows*cols: ## delete unused subplots ##
            fig.delaxes(axes[ax_ind])
            ax_ind += 1

    if not multi_plot:
        plt.legend(lines, labels)

    if scatter:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        if multi_plot:
            bar = fig.colorbar(mappable=sm, ax=axes.ravel().tolist())
        else:
            bar = fig.colorbar(mappable=sm, ax=axes)
        bar.set_label(var)

    plt.figure(figsize=(60,30))
    plt.show()