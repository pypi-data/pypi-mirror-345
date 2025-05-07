import matplotlib.pyplot as plt
import numpy as np
import shutil
from pathlib import Path
from typing import Optional, Tuple, List


class KgnRadar:
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


def radarplot(
    df,
    pathways: List[str],
    figsize: Tuple[int, int] = (8, 8),
    colors: Optional[List[str]] = None,
    sample_order: Optional[List[str]] = None,
    title: Optional[str] = None,
    title_fontsize: float = 14.0,
    title_color: str = "black",
    title_weight: str = "normal",
    title_style: str = "normal",
    title_y: float = 1.1,
    label_fontsize: float = 10.0,
    label_color: str = "black",
    label_weight: str = "normal",
    label_style: str = "normal",
    xtick_background: Optional[str] = None,
    xtick_edgecolor: Optional[str] = None,
    xtick_labelpad: float = 1.05,
    ytick_fontsize: float = 8.0,
    ytick_color: str = "black",
    ytick_weight: str = "normal",
    ytick_alpha: float = 0.5,
    yticklabels: Optional[List[str]] = None,
    fill_alpha: float = 0.25,
    line_width: float = 2.0,
    line_style: str = "solid",
    legend_loc: str = "upper right",
    legend_bbox: Tuple[int, int] = (1.3, 1.1),
    show_legend: bool = True,
):
    """
    Generates a customizable radar (spider) plot for one or more KEGG pathways.

    Parameters:
    - df: Pandas DataFrame containing the dataset.
    - pathways: List of pathway names to be plotted.
    - figsize: Tuple (width, height) of the figure.
    - colors: List of colors for each pathway. If None, default matplotlib colors are used.
    - sample_order: Optional list of sample names. If None, the columns of df will be used.
    - title: Title of the plot.
    - title_fontsize, title_color, title_weight, title_style: Title styling.
    - title_y: Position of the title on the y-axis.
    - label_fontsize, label_color, label_weight, label_style: label styling.
    - xtick_background, xtick_edgecolor, xtick_labelpad: X-axis tick label styling.
    - ytick_fontsize, ytick_color, ytick_weight, ytick_alpha: Y-axis tick label styling.
    - yticklabels: Custom list of labels for the y-axis ticks.
    - fill_alpha: Transparency of the filled areas.
    - line_width, line_style: Line styling.
    - legend_loc: Location of the legend.
    - legend_bbox: Bounding box for the legend.
    - show_legend: Whether to display the legend.

    Returns:
    - Displays a radar plot of the specified pathways across several samples.
    """
    if len(pathways) > 4:
        raise ValueError("Maximum of 4 pathways can be plotted at once.")

    if sample_order is None:
        sample_order = [col for col in df.columns if col != "Function"]

    num_vars = len(sample_order)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Close the loop

    fig, ax = plt.subplots(figsize=figsize, subplot_kw=dict(polar=True))

    if colors is None:
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    # Plot data
    for i, function in enumerate(pathways):
        row = df[df["Function"] == function]
        if row.empty:
            print(f"Warning: Pathway '{function}' not found in DataFrame. Skipping.")
            continue
        values = row[sample_order].values.flatten().tolist()
        values += values[:1]

        ax.plot(
            angles,
            values,
            label=function,
            linewidth=line_width,
            linestyle=line_style,
            color=colors[i % len(colors)],
        )
        ax.fill(
            angles,
            values,
            color=colors[i % len(colors)],
            alpha=fill_alpha,
        )

    # Удаляем стандартные xticks
    ax.set_xticks([])

    # Добавляем серые линии от центра к каждому образцу
    for angle in angles[:-1]:
        ax.plot(
            [angle, angle],
            [0, 1],
            color="lightgray",
            linewidth=1,
            linestyle="solid",
            zorder=0,
        )

    # Добавляем кастомные подписи образцов
    for angle, label in zip(angles[:-1], sample_order):
        ax.text(
            angle,
            xtick_labelpad,  # радиус размещения текста
            label,
            ha="center",
            va="center",
            fontsize=label_fontsize,
            color=label_color,
            fontweight=label_weight,
            style=label_style,
            bbox=(
                dict(
                    facecolor=xtick_background if xtick_background else "none",
                    edgecolor=xtick_edgecolor if xtick_edgecolor else "none",
                    boxstyle="round,pad=0.2",
                )
                if xtick_background or xtick_edgecolor
                else None
            ),
        )

    # Радиальная сетка: задаём значения + видимую внешнюю рамку
    grid_vals = np.linspace(0.2, 1.0, 5)
    ax.set_yticks(grid_vals)
    ax.set_ylim(0, 1.0)

    # Настроим yticklabels для отображения только 0.2 и 1.0
    if yticklabels is None:
        yticklabels = [""] * len(grid_vals)
        yticklabels[grid_vals.tolist().index(0.2)] = "0.2"
        yticklabels[grid_vals.tolist().index(1.0)] = "1.0"

    ax.set_yticklabels(
        yticklabels,
        fontsize=ytick_fontsize,
        color=ytick_color,
        fontweight=ytick_weight,
        alpha=ytick_alpha,
    )

    # Настроим все остальные параметры
    ax.set_yticks(grid_vals)
    ax.set_yticklabels(
        yticklabels,
        fontsize=ytick_fontsize,
        color=ytick_color,
        fontweight=ytick_weight,
        alpha=ytick_alpha,
    )

    # Заголовок и легенда
    plt.title(
        title,
        size=title_fontsize,
        color=title_color,
        weight=title_weight,
        style=title_style,
        y=title_y,
    )
    if show_legend:
        ax.legend(loc=legend_loc, bbox_to_anchor=legend_bbox)

    # Get the path to the current directory (same location as the script)
    current_dir = Path(__file__).resolve().parent
    pycache_dir = current_dir / "__pycache__"

    # Check if __pycache__ exists and remove it
    if pycache_dir.exists() and pycache_dir.is_dir():
        shutil.rmtree(pycache_dir)

    plt.close(fig)

    return KgnRadar(fig, ax)
