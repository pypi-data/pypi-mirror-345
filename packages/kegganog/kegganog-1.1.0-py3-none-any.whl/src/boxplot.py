import matplotlib.pyplot as plt
import seaborn as sns

def boxplot(
    df, 
    figsize=(12, 6), 
    color="blue", 
    showfliers=True,
    title="Distribution of Pathway Completeness Across Samples",
    title_fontsize=16, title_color="black", title_bold=True, title_italic=False,
    xlabel="Samples", xlabel_fontsize=14, xlabel_color="black", xlabel_bold=True, xlabel_italic=False,
    ylabel="Completeness Value", ylabel_fontsize=14, ylabel_color="black", ylabel_bold=True, ylabel_italic=False,
    xticks_rotation=45, xticks_fontsize=12, xticks_color="black", xticks_bold=False, xticks_italic=False,
    yticks_fontsize=12, yticks_color="black", yticks_bold=False, yticks_italic=False,
    grid=True, grid_color="gray", grid_linestyle="--", grid_linewidth=0.5,
    background_color="white"
):
    """
    Generates a highly customizable boxplot for pathway completeness.

    Parameters:
    - df: Pandas DataFrame containing the dataset
    - figsize: Tuple (width, height) of the figure
    - color: Box color
    - showfliers: Boolean, whether to show outliers
    - title: Title of the plot
    - title_fontsize, title_color, title_bold, title_italic: Title styling
    - xlabel, ylabel: Labels for axes
    - xlabel_fontsize, xlabel_color, xlabel_bold, xlabel_italic: X-axis label styling
    - ylabel_fontsize, ylabel_color, ylabel_bold, ylabel_italic: Y-axis label styling
    - xticks_rotation, xticks_fontsize, xticks_color, xticks_bold, xticks_italic: X-ticks styling
    - yticks_fontsize, yticks_color, yticks_bold, yticks_italic: Y-ticks styling
    - grid: Whether to show grid
    - grid_color, grid_linestyle, grid_linewidth: Grid styling
    - background_color: Background color of the figure

    Returns:
    - Displays a boxplot with full customization.
    """

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, facecolor=background_color)

    # Create boxplot
    sns.boxplot(data=df.iloc[:, 1:], color=color, showfliers=showfliers, ax=ax)

    # Customize title
    title_weight = "bold" if title_bold else "normal"
    title_style = "italic" if title_italic else "normal"
    ax.set_title(title, fontsize=title_fontsize, color=title_color, weight=title_weight, style=title_style)

    # Customize x-axis label
    xlabel_weight = "bold" if xlabel_bold else "normal"
    xlabel_style = "italic" if xlabel_italic else "normal"
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize, color=xlabel_color, weight=xlabel_weight, style=xlabel_style)

    # Customize y-axis label
    ylabel_weight = "bold" if ylabel_bold else "normal"
    ylabel_style = "italic" if ylabel_italic else "normal"
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, color=ylabel_color, weight=ylabel_weight, style=ylabel_style)

    # Customize x-ticks
    xtick_weight = "bold" if xticks_bold else "normal"
    xtick_style = "italic" if xticks_italic else "normal"
    plt.xticks(rotation=xticks_rotation, fontsize=xticks_fontsize, color=xticks_color, weight=xtick_weight, style=xtick_style)

    # Customize y-ticks
    ytick_weight = "bold" if yticks_bold else "normal"
    ytick_style = "italic" if yticks_italic else "normal"
    plt.yticks(fontsize=yticks_fontsize, color=yticks_color, weight=ytick_weight, style=ytick_style)

    # Grid settings
    if grid:
        plt.grid(color=grid_color, linestyle=grid_linestyle, linewidth=grid_linewidth)

    # Show plot
    plt.show()