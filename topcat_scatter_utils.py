# Requirements

import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.stats import gaussian_kde

__all__ = ['calculate_density', 'truncate_colormap', 'plot_density_scatter']

# Density Calculation and Sorting Function
def calculate_density(x, y, bandwidth=None):
    """
    Calculate point density for scatter plot data using Gaussian KDE.
    
    Points are sorted by density so that when plotted, denser regions
    appear on top (to emulate TOPCAT plotting behaviour).

    Parameters:
    x : array-like
        X coordinates of the points.
    y : array-like
        Y coordinates of the points.
    bandwidth : float, optional
        Bandwidth for the KDE. If None, it will be estimated automatically.

    Returns:
    x_sorted : array-like
        X coordinates sorted by density.
    y_sorted : array-like
        Y coordinates sorted by density.
    density: array-like
        Density values sorted from least to most dense.

    Raises:
    ValueError
        If x and y have different lengths, if there are fewer than 2 points, or if bandwidth is non-positive.

    Example Usage:
    x = np.random.randn(100)
    y = np.random.randn(100)
    x_sorted, y_sorted, density = calculate_density(x, y)
    """

    x = np.asarray(x)
    y = np.asarray(y)

    # Check same length
    if len(x) != len(y):
        raise ValueError(f"x and y must have same length. Got x: {len(x)}, y: {len(y)}")
    
    # Check minimum points for KDE
    if len(x) < 2:
        raise ValueError(f"Need at least 2 points for density calculation. Got {len(x)}")
    
    if bandwidth is not None and bandwidth <= 0:
        raise ValueError(f"bandwidth must be positive. Got {bandwidth}")
    
    # Handle NaN/inf values
    mask = np.isfinite(x) & np.isfinite(y)
    if not mask.all():
        n_bad = (~mask).sum()
        warnings.warn(f"Removing {n_bad} points with NaN or infinite values")
        x = x[mask]
        y = y[mask]
    
    xy = np.vstack([x, y])
    z = gaussian_kde(xy, bw_method=bandwidth)(xy) # Evaluate density

    idx = z.argsort()  
    x_sorted, y_sorted, density = x[idx], y[idx], z[idx] # Sort points by density

    return x_sorted, y_sorted, density

def truncate_colormap(cmap, minval=0.4, maxval=0.9, n=256):
    """
    Truncate a matplotlib colormap to a specified range.

    Used in this script to avoid the light and dark extremes of colormaps
    to better emulate the TOPCAT density style.
    
    Parameters:
    cmap : matplotlib.colors.Colormap OR str
        The original colormap to be truncated. Can be a colormap object or a string name of a colormap.
    minval : float, default=0.4
        The minimum value of the colormap to include (between 0 and 1).
    maxval : float, default=0.9
        The maximum value of the colormap to include (between 0 and 1).
    n : int, default=256
        The number of discrete colors to generate in the truncated colormap.
    
    Returns:
    LinearSegmentedColormap
        The truncated colormap.

    Validates:
        - minval must be less than maxval.
        - minval and maxval must be between 0 and 1.

    Example Usage:
    truncated_cmap = truncate_colormap('viridis', 0.2, 0.8)
    # or
    original_cmap = plt.get_cmap('viridis')
    truncated_cmap = truncate_colormap(original_cmap, 0.2, 0.8)
    """

    # Allow string input (e.g., 'Reds' instead of plt.get_cmap('Reds'))
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)
    
    # Validate range
    if minval >= maxval:
        raise ValueError(f"minval must be less than maxval. Got minval={minval}, maxval={maxval}")
    
    if not (0 <= minval <= 1 and 0 <= maxval <= 1):
        raise ValueError(f"minval and maxval must be between 0 and 1. Got minval={minval}, maxval={maxval}")
    
    new_cmap = mcolors.LinearSegmentedColormap.from_list(
        'truncated({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n))
    )
    return new_cmap

def plot_density_scatter(x, y, bandwidth=None, cmap='Reds', 
                         minval=0.4, maxval=0.9, n=256, ax=None, **scatter_kwargs):
    """
    Create a density scatter plot similar to TOPCAT's density plot style.

     This is a convenience function combining calculate_density() and
    truncate_colormap(). For more control, use those functions separately.
    By default, edgecolor is set to 'none' to match TOPCAT style.

    Parameters:
    x : array-like
        X coordinates of the points.
    y : array-like
        Y coordinates of the points.
    bandwidth : float, optional
        Bandwidth for the KDE. If None, it will be estimated automatically.
    cmap : str or matplotlib.colors.Colormap, default='Reds'
        Colormap to use for density coloring.
    minval : float, default=0.4
        Minimum value for truncating the colormap.
    maxval : float, default=0.9
        Maximum value for truncating the colormap.
    n : int, default=256
        The number of discrete colors to generate in the truncated colormap.
    ax : matplotlib.axes.Axes, optional
        Axes object to plot on. If None, uses current axes.
    **scatter_kwargs : keyword arguments
        Additional keyword arguments passed to plt.scatter().
    
    Returns:
    scatter : matplotlib.collections.PathCollection
        The scatter plot object.

    Example Usage:
    x = np.random.randn(1000)
    y = np.random.randn(1000)
    cmap='viridis'
    plot_density_scatter(x, y, cmap=cmap, minval=0.2, maxval=0.8)
    """

    x_sorted, y_sorted, density = calculate_density(x, y, bandwidth)
    truncated_cmap = truncate_colormap(cmap, minval, maxval, n)

    if ax is None:
        ax = plt.gca() 
    
    # Set default edgecolor if not specified by user
    scatter_kwargs.setdefault('edgecolor', 'None')
    
    scatter = ax.scatter(x_sorted, y_sorted, c=density, 
                         cmap=truncated_cmap, **scatter_kwargs)
    return scatter
