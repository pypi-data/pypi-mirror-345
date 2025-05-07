from pathlib import Path
from typing import Optional, Tuple, Union
import matplotlib.pyplot as plt
import seaborn as sns
import shutil
import pandas as pd


class KgnBoxplot:
    def __init__(self, fig: plt.Figure, ax: plt.Axes):
        self.fig = fig
        self.ax = ax

    def plotfig(self) -> plt.Figure:
        self.fig.tight_layout()
        plt.show()
        return self.fig

    def savefig(self, path: str, dpi: int = 300, bbox_inches: str = "tight"):
        """
        Save the figure to a file.

        Parameters:
        - path: Path to save the figure (e.g. "plot.png", "plot.svg").
        - dpi: Dots per inch (resolution) of the output image. Default is 300.
        - bbox_inches: Bounding box option passed to matplotlib. Default is "tight".
        """
        self.fig.savefig(path, dpi=dpi, bbox_inches=bbox_inches)


def boxplot(
    df,
    figsize: Tuple[int, int] = (12, 6),
    color: Optional[str] = "blue",
    showfliers: bool = True,
    title: Optional[str] = None,
    title_fontsize: float = 16.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    xlabel: str = "Samples",
    xlabel_fontsize: float = 14.0,
    xlabel_color: str = "black",
    xlabel_weight: str = "normal",
    xlabel_style: str = "normal",
    ylabel: str = "Completeness Value",
    ylabel_fontsize: float = 14.0,
    ylabel_color: str = "black",
    ylabel_weight: str = "normal",
    ylabel_style: str = "normal",
    xticks_rotation: float = 45.0,
    xticks_fontsize: float = 12.0,
    xticks_color: str = "black",
    xtick_weight: str = "normal",
    xtick_style: str = "normal",
    yticks_fontsize: float = 12.0,
    yticks_color: str = "black",
    ytick_weight: str = "normal",
    ytick_style: str = "normal",
    grid: bool = True,
    grid_color: str = "gray",
    grid_linestyle: str = "--",
    grid_linewidth: float = 0.5,
    background_color: str = "white",
):
    """
    Generates a customizable boxplot to visualize the distribution of pathway completeness across samples.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - figsize: Tuple (width, height) of the figure.
    - color: Color used for all boxes in the plot. Can be a named color (e.g., "blue"), hex code (e.g., "#1f77b4").
    - showfliers: Whether to display outlier points.
    - title: Main title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title text styling.
    - xlabel, ylabel: Axis labels.
    - xlabel_fontsize, xlabel_color, xlabel_weight, xlabel_style: X-axis label styling.
    - ylabel_fontsize, ylabel_color, ylabel_weight, ylabel_style: Y-axis label styling.
    - xticks_rotation: Rotation angle of x-axis tick labels.
    - xticks_fontsize, xticks_color, xtick_weight, xtick_style: X-axis tick label styling.
    - yticks_fontsize, yticks_color, ytick_weight, ytick_style: Y-axis tick label styling.
    - grid: Whether to display a grid.
    - grid_color, grid_linestyle, grid_linewidth: Grid styling.
    - background_color: Background color of the figure.

    Returns:
    - Displays a boxplot of pathway completeness.
    """

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    # Create boxplot
    sns.boxplot(data=df.iloc[:, 1:], color=color, showfliers=showfliers, ax=ax)

    # Customize title
    ax.set_title(
        title,
        fontsize=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
    )

    # Customize x-axis label
    ax.set_xlabel(
        xlabel,
        fontsize=xlabel_fontsize,
        color=xlabel_color,
        weight=xlabel_weight,
        style=xlabel_style,
    )

    # Customize y-axis label
    ax.set_ylabel(
        ylabel,
        fontsize=ylabel_fontsize,
        color=ylabel_color,
        weight=ylabel_weight,
        style=ylabel_style,
    )

    # Customize x-ticks
    plt.xticks(
        rotation=xticks_rotation,
        fontsize=xticks_fontsize,
        color=xticks_color,
        weight=xtick_weight,
        style=xtick_style,
    )

    # Customize y-ticks
    plt.yticks(
        fontsize=yticks_fontsize,
        color=yticks_color,
        weight=ytick_weight,
        style=ytick_style,
    )

    # Grid settings
    if grid:
        plt.grid(color=grid_color, linestyle=grid_linestyle, linewidth=grid_linewidth)

    # Clean up __pycache__
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnBoxplot(fig, ax)
