import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from torchmetrics import PearsonCorrCoef, SpearmanCorrCoef

def preds2scatter(
    predictions,
    real_results,
    patients,
    folds,
    output_path=None,
    density_bins=(1000, 1000),
    cmap='turbo',
    marker='.',
    marker_size=4,
    best_fit_line=True,
    title='Density Scatter Plot',
    title_fontsize=30,
    xlabel='Real Response',
    xlabel_fontsize=25,
    ylabel='Predicted Response',
    ylabel_fontsize=25,
    xtick_fontsize=12,
    ytick_fontsize=12,
    x_range=None,
    y_range=None,
    display_plot=True,
    verbose=True,
    show_legend=True,
    legend_position=(1.05, 0.5),
    annotation_fontsize=13,
    transparent_bg=True,
    plot_size=(8, 8)
):
    """
    Generate a density scatter plot comparing real vs. predicted drug response values
    with detailed statistical metrics for drug response prediction evaluation.

    Parameters
    ----------
    predictions : array-like, shape (n_samples,)
        Predicted drug response values.
    real_results : array-like, shape (n_samples,)
        Actual (true) response values for each sample.
    patients : array-like, shape (n_samples,)
        Patient ID/name for each sample.
    folds : array-like, shape (n_samples,)
        Cross-validation fold identifiers.
    output_path : str, optional
        File path to save the plot. If None, the plot is not saved.
    density_bins : tuple of (int, int), default=(1000, 1000)
        Number of bins for density calculation (x_bins, y_bins).
    cmap : str, default='turbo'
        Matplotlib colormap name for density visualization.
    marker : str, default='.'
        Scatter plot marker style.
    marker_size : int, default=4
        Size of scatter plot markers.
    best_fit_line : bool, default=True
        Whether to show the linear regression line.
    title : str, default='Density Scatter Plot'
        Plot title.
    title_fontsize : int, default=30
        Font size for the plot title.
    xlabel : str, default='Real Response'
        X-axis label.
    xlabel_fontsize : int, default=25
        Font size for the X-axis label.
    ylabel : str, default='Predicted Response'
        Y-axis label.
    ylabel_fontsize : int, default=25
        Font size for the Y-axis label.
    xtick_fontsize : int, default=12
        Font size for the X-axis ticks.
    ytick_fontsize : int, default=12
        Font size for the Y-axis ticks.
    x_range : tuple of (float, float), optional
        X-axis range (min, max).
    y_range : tuple of (float, float), optional
        Y-axis range (min, max).
    display_plot : bool, default=True
        Whether to display the plot.
    verbose : bool, default=True
        Whether to print metric values in a table format.
    show_legend : bool, default=True
        Whether to show metrics in the legend.
    legend_position : tuple of (float, float), default=(1.05, 0.5)
        Legend position relative to the plot.
    annotation_fontsize : int, default=13
        Font size for metric annotations in the legend.
    transparent_bg : bool, default=False
        Whether to save the plot with a transparent background.
    plot_size : tuple of (float, float), default=(8, 8)
        Size of the plot in inches.

    Returns
    -------
    dict
        Dictionary containing computed metrics:
        - overall_spearman: Overall Spearman correlation coefficient.
        - overall_pearson: Overall Pearson correlation coefficient.
        - mse_loss: Mean squared error between real and predicted values.
        - average_spearman: Average Spearman correlation across folds.
        - average_pearson: Average Pearson correlation across folds.
    """
    
    # --- Input Validation and Conversion ---
    x = np.asarray(real_results).flatten() if not isinstance(real_results, np.ndarray) else real_results.flatten()
    y = np.asarray(predictions).flatten() if not isinstance(predictions, np.ndarray) else predictions.flatten()
    patients = np.asarray(patients).flatten() if not isinstance(patients, np.ndarray) else patients.flatten()
    folds = np.asarray(folds).flatten() if not isinstance(folds, np.ndarray) else folds.flatten()
    
    if not (len(x) == len(y) == len(patients) == len(folds)):
        raise ValueError("All input arrays must have the same length.")
    
    pearson_corr = PearsonCorrCoef()
    spearman_corr = SpearmanCorrCoef()
    
    df = pd.DataFrame({
        'Real': x,
        'Predicted': y,
        'patients': patients,
        'Fold': folds
    })
    
    x_tensor = torch.tensor(x, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    
    overall_pearson = pearson_corr(x_tensor, y_tensor).item()
    overall_spearman = spearman_corr(x_tensor, y_tensor).item()
    mse_loss = nn.MSELoss()(y_tensor, x_tensor).item()
    
    fold_pearsons = []
    fold_spearmans = []
    for fold, group in df.groupby('Fold'):
        x_fold = group['Real'].to_numpy()
        y_fold = group['Predicted'].to_numpy()
        if len(x_fold) < 2:
            continue
        x_fold_tensor = torch.tensor(x_fold, dtype=torch.float32)
        y_fold_tensor = torch.tensor(y_fold, dtype=torch.float32)
        fold_pearsons.append(pearson_corr(x_fold_tensor, y_fold_tensor).item())
        fold_spearmans.append(spearman_corr(x_fold_tensor, y_fold_tensor).item())
    
    if fold_pearsons and fold_spearmans:
        avg_pearson = np.mean(fold_pearsons)
        avg_spearman = np.mean(fold_spearmans)
    
    hh, locx, locy = np.histogram2d(x, y, bins=density_bins)
    x_bin_idx = np.digitize(x, locx) - 1
    y_bin_idx = np.digitize(y, locy) - 1
    x_bin_idx = np.clip(x_bin_idx, 0, hh.shape[0] - 1)
    y_bin_idx = np.clip(y_bin_idx, 0, hh.shape[1] - 1)
    z = hh[x_bin_idx, y_bin_idx]
    
    idx = z.argsort()
    x_sorted, y_sorted, z_sorted = x[idx], y[idx], z[idx]
    
    fig, ax = plt.subplots(figsize=plot_size)
    scatter = ax.scatter(x_sorted, y_sorted, c=z_sorted, cmap=cmap,
                         marker=marker, s=marker_size)
    
    if best_fit_line:
        m, b_line = np.polyfit(x, y, 1)
        ax.plot(x, m * x + b_line, color='#333333', linewidth=1.5)
    
    ax.tick_params(axis='x', labelsize=xtick_fontsize)
    ax.tick_params(axis='y', labelsize=ytick_fontsize)
    ax.set_xlabel(xlabel, labelpad=18, color='#333333', fontsize=xlabel_fontsize)
    ax.set_ylabel(ylabel, labelpad=18, color='#333333', fontsize=ylabel_fontsize)
    ax.set_title(title, color='#000000', weight='bold', fontsize=title_fontsize)
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
        
    if show_legend:
        metrics_label = (f"MSE Loss = {mse_loss:.2f}\n"
                         f"Average Fold's SCC = {avg_spearman:.2f}\n"
                         f"Average Fold's PCC = {avg_pearson:.2f}\n"
                         f"Overall SCC = {overall_spearman:.2f}\n"
                         f"Overall PCC = {overall_pearson:.2f}"
                         )
        dummy = Line2D([], [], linestyle='None', marker='o', markersize=0, color='none', label=metrics_label)
        ax.legend(handles=[dummy], loc='center left', bbox_to_anchor=legend_position,
                  fontsize=annotation_fontsize, handlelength=0, handletextpad=0)
    
    fig.tight_layout()
    
    if output_path:
        fig.savefig(output_path, transparent=transparent_bg, bbox_inches='tight', dpi=350)
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
    
    return {
        'overall_spearman': overall_spearman,
        'overall_pearson': overall_pearson,
        'mse_loss': mse_loss,
        'average_spearman': avg_spearman,
        'average_pearson': avg_pearson
    }

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

# --- Synthetic Data Generation ---

# Set a random seed for reproducibility.
np.random.seed(42)

# Number of samples
num_samples = 200

# Generate synthetic real response values (e.g., uniformly distributed between 0 and 100)
real_results = np.random.uniform(0, 100, num_samples)

# Generate predictions as the real response with some added Gaussian noise
predictions = real_results + np.random.normal(0, 10, num_samples)

# Randomly assign each sample a drug from a list of five drugs.
drugs_list = ["Drug A", "Drug B", "Drug C", "Drug D", "Drug E"]
drugs = np.random.choice(drugs_list, num_samples).tolist()

# Randomly assign each sample a cancer type from a list of three types.
cancers_list = ["Cancer X", "Cancer Y", "Cancer Z"]
cancers = np.random.choice(cancers_list, num_samples).tolist()

# Randomly assign each sample a fold identifier from a list of five folds.
folds_list = ["Fold 1", "Fold 2", "Fold 3", "Fold 4", "Fold 5"]
folds = np.random.choice(folds_list, num_samples).tolist()

# --- Call the preds2scatter Function ---
# Assuming the preds2scatter function is defined above, we call it with our test data.

metrics = preds2scatter(predictions, drugs, cancers, real_results, folds,
                        output_path='scatter.png', bins=(50,50), cmap='viridis',
                        marker='o', marker_size=5, best_fit_line=True,
                        title='Test Density Scatter Plot',
                        xlabel='True Response', ylabel='Predicted Response',
                        annotation_fontsize=12,
                        display_plot=True, verbose=True, show_legend=True)



