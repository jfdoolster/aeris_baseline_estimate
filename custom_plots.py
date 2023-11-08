import matplotlib.pyplot as plt

def set_custom_rcparams(grid=True):
    """
    custom rcparams
    """
    plt.rcParams['axes.grid'] = grid
    plt.rcParams['lines.linewidth'] = 1.5
    plt.rcParams['legend.loc'] = "upper left"
    # Set the default text font size
    plt.rc('font', size=12)
    # Set the axes title font size
    plt.rc('axes', titlesize=16)
    # Set the axes labels font size
    plt.rc('axes', labelsize=14)
    # Set the font size for x tick labels
    plt.rc('xtick', labelsize=12)
    # Set the font size for y tick labels
    plt.rc('ytick', labelsize=12)
    # Set the legend font size
    plt.rc('legend', fontsize=10)
    # Set the font size of the figure title
    plt.rc('figure', titlesize=16)