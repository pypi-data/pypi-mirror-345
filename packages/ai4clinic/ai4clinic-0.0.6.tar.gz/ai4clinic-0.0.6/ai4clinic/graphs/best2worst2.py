import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import torch
import torch.nn as nn
from torchmetrics import PearsonCorrCoef, SpearmanCorrCoef

def best2worst2(
    predictions,
    real_results,
    drugs,
    patients,
    folds,
    plot_size=(8, 10),
    corr_metric='spearman',
    num_select=2,
    output_path=None,
    marker='.',
    marker_size=4,
    best_fit_line=True,
    title=None,
    xlabel='Real Response',
    ylabel='Predicted Response',
    annotation_fontsize=13,
    worst_color_hex=None,
    best_color_hex=None,
    display_plot=True,
    verbose=True,
    show_legend=True,
    show_metrics=False,
    legend_position='upper right',
    title_fontsize=30,
    xlabel_fontsize=25,
    ylabel_fontsize=25,
    xtick_fontsize=12,
    ytick_fontsize=12,
    x_range=None,
    y_range=None,
    transparent_bg=True
):
    """
    Generate a plot with the best and worst predictions linear regressions based on correlation metrics with detailed statistical metrics for drug response prediction evaluation if desired.

    Parameters
    ----------
    predictions : array-like, shape (n_samples,)
        Predicted drug response values.
    real_results : array-like, shape (n_samples,)
        Actual (true) response values for each sample.
    drugs : array-like, shape (n_samples,)
        Drug ID/name for each sample.
    patients : array-like, shape (n_samples,)
        Patient/cell ID/name for each sample.
    folds : array-like, shape (n_samples,)
        Cross-validation fold identifiers.
    plot_size : tuple of (float, float), default=(8, 10)
        Size of the plot in inches.
    corr_metric : str, default='pearson'
        Correlation metric to use ('pearson' or 'spearman').
    num_select : int, default=2
        Number of best and worst predictions to highlight.
    output_path : str, optional
        File path to save the plot. If None, the plot is not saved.
    marker : str, default='.'
        Scatter plot marker style.
    marker_size : int, default=4
        Size of scatter plot markers.
    best_fit_line : bool, default=True
        Whether to show the linear regression line.
    title : str, optional
        Plot title.
    xlabel : str, default='Real Response'
        X-axis label.
    xlabel_fontsize : int, default=25
        Font size for the X-axis label.
    ylabel : str, default='Predicted Response'
        Y-axis label.
    ylabel_fontsize : int, default=25
        Font size for the Y-axis label.
    annotation_fontsize : int, default=13
        Font size for annotations.
    worst_color_hex : str, optional
        Hex color for worst predictions annotation.
    best_color_hex : str, optional
        Hex color for best predictions annotation.
    display_plot : bool, default=True
        Whether to display the plot.
    verbose : bool, default=True
        Whether to print additional information.
    show_legend : bool, default=True
        Whether to show metrics in the legend.
    show_metrics : bool, default=False
        Whether to display metric values.
    legend_position : str or tuple, default='upper right'
        Legend position on the plot.
    title_fontsize : int, default=30
        Font size for the plot title.
    xtick_fontsize : int, default=12
        Font size for the X-axis ticks.
    ytick_fontsize : int, default=12
        Font size for the Y-axis ticks.
    x_range : tuple of (float, float), optional
        X-axis range (min, max).
    y_range : tuple of (float, float), optional
        Y-axis range (min, max).
    transparent_bg : bool, default=True
        Whether to save the plot with a transparent background.

    Returns
    -------
    fig, ax : matplotlib.figure.Figure, matplotlib.axes.Axes
        The figure and axes of the generated plot.
    """

    # Convert inputs to numpy arrays if they are not already
    real_results = np.asarray(real_results).flatten() if not isinstance(real_results, np.ndarray) else real_results.flatten()
    predictions = np.asarray(predictions).flatten() if not isinstance(predictions, np.ndarray) else predictions.flatten()
    drugs = np.asarray(drugs).flatten() if not isinstance(drugs, np.ndarray) else drugs.flatten()
    patients = np.asarray(patients).flatten() if not isinstance(patients, np.ndarray) else patients.flatten()
    folds = np.asarray(folds).flatten() if not isinstance(folds, np.ndarray) else folds.flatten()
    
    n = len(predictions)
    if not (len(real_results) == len(drugs) == len(patients) == len(folds) == n):
        raise ValueError("All input lists must be of equal length.")
    if num_select not in [1, 2, 3, 4, 5]:
        raise ValueError("num_select must be 1, 2, 3, 4, or 5")
    if corr_metric.lower() not in ['pearson', 'spearman']:
        raise ValueError("corr_metric must be either 'pearson' or 'spearman'")
    
    if title is None:
        title = f"Overall {corr_metric.capitalize()} Correlation"
    
    df = pd.DataFrame({
        'Predicted': predictions,
        'Real': real_results,
        'Drug': drugs,
        'Cell': patients,  
        'Fold': folds
    })
    
    pearson_corr = PearsonCorrCoef()
    spearman_corr = SpearmanCorrCoef()
    
    real_tensor = torch.tensor(real_results, dtype=torch.float32)
    predictions_tensor = torch.tensor(predictions, dtype=torch.float32)
    
    overall_pearson = pearson_corr(predictions_tensor, real_tensor)
    overall_spearman = spearman_corr(predictions_tensor, real_tensor)
    mse_loss = nn.MSELoss()(real_tensor, real_tensor).item()
    
    fold_pearsons = []
    fold_spearmans = []
    for fold, group in df.groupby('Fold'):
        if len(group) < 2:
            continue
        p = pearson_corr(torch.tensor(group['Predicted'].to_numpy(), dtype=torch.float32), 
                         torch.tensor(group['Real'].to_numpy(), dtype=torch.float32))
        s = spearman_corr(torch.tensor(group['Predicted'].to_numpy(), dtype=torch.float32), 
                          torch.tensor(group['Real'].to_numpy(), dtype=torch.float32))
        fold_pearsons.append(p)
        fold_spearmans.append(s)
    
    avg_pearson = np.mean(fold_pearsons) if fold_pearsons else overall_pearson
    avg_spearman = np.mean(fold_spearmans) if fold_spearmans else overall_spearman
    
    drug_avg_corr = {}
    unique_drugs = df['Drug'].unique()
    for drug in unique_drugs:
        df_drug = df[df['Drug'] == drug]
        fold_corrs = []
        for fold_id, group in df_drug.groupby('Fold'):
            if len(group) < 2:
                continue
            if corr_metric.lower() == 'pearson':
                c = pearson_corr(torch.tensor(group['Predicted'].to_numpy(), dtype=torch.float32), 
                                 torch.tensor(group['Real'].to_numpy(), dtype=torch.float32))
            else:
                c = spearman_corr(torch.tensor(group['Predicted'].to_numpy(), dtype=torch.float32), 
                                  torch.tensor(group['Real'].to_numpy(), dtype=torch.float32))
            fold_corrs.append(c)
        drug_avg_corr[drug] = round(np.mean(fold_corrs), 4) if fold_corrs else None
    
    valid_drugs = {drug: corr for drug, corr in drug_avg_corr.items() if corr is not None}
    
    selected_drugs = []
    color_map = {}
    if len(valid_drugs) >= 2 * num_select:
        sorted_drugs = sorted(valid_drugs.items(), key=lambda x: x[1])
        worst_drugs = [drug for drug, _ in sorted_drugs[:num_select]]
        best_drugs = [drug for drug, _ in sorted_drugs[-num_select:]]
        selected_drugs.extend(worst_drugs + best_drugs)
        if worst_color_hex is not None:
            for drug in worst_drugs:
                color_map[drug] = worst_color_hex
        else:
            from matplotlib import cm
            worst_colors = cm.Reds(np.linspace(0.6, 0.9, num_select))
            for i, drug in enumerate(worst_drugs):
                color_map[drug] = worst_colors[i]
        if best_color_hex is not None:
            for drug in best_drugs:
                color_map[drug] = best_color_hex
        else:
            from matplotlib import cm
            best_colors = cm.Greens(np.linspace(0.6, 0.9, num_select))
            for i, drug in enumerate(best_drugs):
                color_map[drug] = best_colors[i]
    elif len(valid_drugs) >= 2:
        sorted_drugs = sorted(valid_drugs.items(), key=lambda x: x[1])
        selected_drugs = [sorted_drugs[0][0], sorted_drugs[-1][0]]
        color_map[selected_drugs[0]] = worst_color_hex if worst_color_hex is not None else '#8B0000'
        color_map[selected_drugs[1]] = best_color_hex if best_color_hex is not None else '#006400'
    else:
        if verbose:
            print("Warning: Not enough valid drugs with sufficient fold data; only overall metrics will be displayed.")
    
    fig, ax = plt.subplots(figsize=plot_size)
    ax.scatter(real_results, predictions_tensor.numpy(), c="#ABBCBF", marker=marker, s=marker_size * 8)
    
    if best_fit_line:
        m, b_line = np.polyfit(real_results, predictions_tensor.numpy(), 1)
        ax.plot(real_results, m * df['Real'] + b_line, color='#333333', linewidth=1.5)
    
    # Counter to alternate text positions
    alternate = True

    for drug in selected_drugs:
        df_drug = df[df['Drug'] == drug]
        if df_drug.empty:
            continue
        x_d = df_drug['Real'].to_numpy()
        y_d = df_drug['Predicted'].to_numpy()
        ax.scatter(x_d, y_d, c=[color_map[drug]], marker=marker, s=marker_size * 8,
           label=f"{drug} ({valid_drugs[drug]:.2f})")
        if len(x_d) > 1:
            m_d, b_d = np.polyfit(x_d, y_d, 1)
        
            # Extend the x range slightly for extrapolation
            x_min, x_max = np.min(x_d), np.max(x_d)
            x_range_extension = (x_max - x_min) * 0.2  # Extend by 10% of the range
            x_line = np.linspace(x_min - x_range_extension, x_max + x_range_extension, 100)
            y_line = m_d * x_line + b_d
            ax.plot(x_line, y_line, color=color_map[drug], linewidth=4)

            # Calculate the position on the regression line for the mean x value
            mean_x = np.mean(x_d)
            mean_y_on_line = m_d * mean_x + b_d

            # Alternate the horizontal alignment of text
            ha = 'right' if alternate else 'left'
            ax.text(mean_x+0.01, mean_y_on_line, f"{valid_drugs[drug]:.2f}",
                    fontsize=annotation_fontsize, color='#000000', weight='bold',
                    ha=ha, va='bottom', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', pad=0.1))

            # Toggle the alternate flag
            alternate = not alternate
    
    ax.tick_params(axis='x', labelsize=xtick_fontsize)
    ax.tick_params(axis='y', labelsize=ytick_fontsize)
    ax.set_xlabel(xlabel, fontsize=xlabel_fontsize, color='#333333', labelpad=18)
    ax.set_ylabel(ylabel, fontsize=ylabel_fontsize, color='#333333', labelpad=18)
    ax.set_title(title, fontsize=title_fontsize, color='#000000', weight='bold')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#DDDDDD')
    ax.spines['left'].set_color('#DDDDDD')
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#EEEEEE')
    
    if x_range is not None:
        ax.set_xlim(x_range)
    if y_range is not None:
        ax.set_ylim(y_range)
    
    overall_metrics = (f"Overall Spearman = {overall_spearman:.3f}\n"
                       f"Overall Pearson = {overall_pearson:.3f}\n"
                       f"MSE Loss = {mse_loss:.3f}\n"
                       f"Avg Fold Spearman = {avg_spearman:.3f}\n"
                       f"Avg Fold Pearson = {avg_pearson:.3f}")
    if show_legend:
        dummy = Line2D([], [], linestyle='None', marker='o', markersize=0,
                       color='none', label=overall_metrics)
        handles, labels = ax.get_legend_handles_labels()
        handles.append(dummy)
        if show_metrics:
            labels.append(overall_metrics)
        ax.legend(handles=handles, labels=labels, loc=legend_position, fontsize=annotation_fontsize,
             title=None, title_fontsize=annotation_fontsize, markerscale=5, handletextpad=0.02)
    
    fig.tight_layout()
    
    if output_path:
        fig.savefig(output_path, transparent=transparent_bg, bbox_inches='tight')
    if display_plot:
        plt.show()
    else:
        plt.close(fig)
    
    if verbose:
        try:
            from rich.console import Console
            from rich.table import Table
            
            console = Console()
            table = Table(title="Performance Metrics")
            
            table.add_column("Metric", style="cyan")
            table.add_column("Value", justify="right", style="green")
            
            table.add_row("Overall Spearman", f"{overall_spearman:.3f}")
            table.add_row("Overall Pearson", f"{overall_pearson:.3f}")
            table.add_row("MSE Loss", f"{mse_loss:.3f}")
            table.add_row("Avg Fold Spearman", f"{avg_spearman:.3f}")
            table.add_row("Avg Fold Pearson", f"{avg_pearson:.3f}")
            
            console.print(table)
        except ImportError:
            print(f"Overall Spearman = {overall_spearman:.3f}")
            print(f"Overall Pearson = {overall_pearson:.3f}")
            print(f"MSE Loss = {mse_loss:.3f}")
            print(f"Avg Fold Spearman = {avg_spearman:.3f}")
            print(f"Avg Fold Pearson = {avg_pearson:.3f}")
    
    return fig, ax
