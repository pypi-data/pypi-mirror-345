import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from torchmetrics import PearsonCorrCoef, SpearmanCorrCoef

def drugs2waterfall(
    predictions,
    real_results,
    drugs,
    patients,
    folds,
    plot_size=(20, 8),
    output_path=None,
    corr_metric='spearman',
    num_select=10,
    mark_threshold=0.5,
    color=None,
    display_plot=True,
    percentage_position=(0.2, 0.5),
    percentage_fontsize=60,
    ylabel='Correlation',
    ylabel_fontsize=20,
    xlabel='Drugs',
    xlabel_fontsize=20,
    title='Drug Response Correlations',
    title_fontsize=20,
    ytick_fontsize=15,
    transparent_bg=True,
    bar_annotation_fontsize=18,
    drug_name_fontsize=16,
    ax2_ylim=None,
    ax2_title='Top Drugs by Correlation',
    legend_position='lower left',
    legend_fontsize=12,
    legend=True
):
    """
    Generate a waterfall plot of drug response correlations.

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
    plot_size : tuple of (float, float), default=(20, 8)
        Size of the plot in inches.
    output_path : str, optional
        File path to save the plot. If None, the plot is not saved.
    corr_metric : str, default='spearman'
        Correlation metric to use ('pearson' or 'spearman').
    num_select : int, default=10
        Number of top correlations to display.
    mark_threshold : float, default=0.5
        Threshold to mark significant correlations.
    color : str, optional
        Color of the bars.
    display_plot : bool, default=True
        Whether to display the plot.
    percentage_position : tuple of (float, float), default=(0.2, 0.5)
        Position for percentage annotations.
    percentage_fontsize : int, default=60
        Font size for percentage annotations.
    ylabel : str, default='Correlation'
        Y-axis label.
    ylabel_fontsize : int, default=20
        Font size for the Y-axis label.
    xlabel : str, default='Drugs'
        X-axis label.
    xlabel_fontsize : int, default=20
        Font size for the X-axis label.
    title : str, default='Drug Response Correlations'
        Plot title.
    title_fontsize : int, default=20
        Font size for the plot title.
    ytick_fontsize : int, default=15
        Font size for the Y-axis ticks.
    transparent_bg : bool, default=True
        Whether to save the plot with a transparent background.
    bar_annotation_fontsize : int, default=18
        Font size for bar annotations.
    drug_name_fontsize : int, default=16
        Font size for drug name annotations.
    ax2_ylim : tuple of (float, float), optional
        Y-axis limits for the secondary axis.
    ax2_title : str, optional
        Title for the secondary axis.
    legend_position : str or tuple, default='lower left'
        Legend position on the plot.
    legend_fontsize : int, default=12
        Font size for the legend text.
    legend : bool, default=True
        Whether to display a legend.

    Returns
    -------
    fig, axes : matplotlib.figure.Figure, matplotlib.axes.Axes
        The figure and axes of the generated plot.
    """
    
    # Convert inputs to numpy arrays if they are not already
    real_results = np.asarray(real_results).flatten() if not isinstance(real_results, np.ndarray) else real_results.flatten()
    predictions = np.asarray(predictions).flatten() if not isinstance(predictions, np.ndarray) else predictions.flatten()
    patients = np.asarray(patients).flatten() if not isinstance(patients, np.ndarray) else patients.flatten()
    drugs = np.asarray(drugs).flatten() if not isinstance(drugs, np.ndarray) else drugs.flatten()
    folds = np.asarray(folds).flatten() if not isinstance(folds, np.ndarray) else folds.flatten()
    
    # Validate inputs
    if not (len(predictions) == len(real_results) == len(drugs) == len(patients) == len(folds)):
        raise ValueError("All input lists must have the same length.")
    if corr_metric not in ['pearson', 'spearman']:
        raise ValueError("corr_metric must be either 'pearson' or 'spearman'.")
    
    # Create DataFrame
    df = pd.DataFrame({
        'Predictions': predictions,
        'Real_Results': real_results,
        'Drugs': drugs,
        'patients': patients,
        'Folds': folds
    })
    
    # Instantiate torchmetrics correlation coefficient classes
    pearson_corr = PearsonCorrCoef()
    spearman_corr = SpearmanCorrCoef()

    drug_avg_corr = {}
    unique_drugs = df['Drugs'].unique()
    for drug in unique_drugs:
        df_drug = df[df['Drugs'] == drug]
        fold_corrs = []
        for fold_id, group in df_drug.groupby('Folds'):
            if len(group) < 2:
                continue
            if corr_metric.lower() == 'pearson':
                c = pearson_corr(torch.tensor(group['Predictions'].to_numpy(), dtype=torch.float32), 
                                 torch.tensor(group['Real_Results'].to_numpy(), dtype=torch.float32))
            else:
                c = spearman_corr(torch.tensor(group['Predictions'].to_numpy(), dtype=torch.float32), 
                                  torch.tensor(group['Real_Results'].to_numpy(), dtype=torch.float32))
            fold_corrs.append(c)
        drug_avg_corr[drug] = round(np.mean(fold_corrs), 4) if fold_corrs else None
    
    valid_drugs = {drug: corr for drug, corr in drug_avg_corr.items() if corr is not None}
    
    drug_corrs = pd.Series(valid_drugs).sort_values(ascending=False)
    
    # Calculate the percentage of drugs with a correlation greater than mark_threshold
    percentage = round((sum(drug_corrs >= mark_threshold) / len(drug_corrs)) * 100)
    
    # Define colors
    highlight_color = color if color else '#B4D04F'
    default_color = '#C9C9C9'
    
    # Set up figure with two subplots side-by-side
    fig, axes = plt.subplots(1, 2, figsize=plot_size)
    ax1, ax2 = axes
    
    # Waterfall plot (from best to worst, left to right)
    colors = [highlight_color if corr >= mark_threshold else default_color for corr in drug_corrs.values]
    ax1.bar(drug_corrs.index, drug_corrs.values, color=colors, edgecolor=colors, linewidth=1)
    
    ax1.set_xticks([])
    ax1.set_ylabel(ylabel, fontsize=ylabel_fontsize)
    ax1.set_xlabel(xlabel, fontsize=xlabel_fontsize)
    ax1.set_title(title, fontsize=title_fontsize, fontweight='bold')
    
    # Display percentage text on the waterfall plot
    ax1.text(percentage_position[0], percentage_position[1], f"{percentage}%", fontsize=percentage_fontsize,
             color='#000000', transform=ax1.transAxes, ha='center', va='center')
    
    # Remove unnecessary spines
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    
    # Customize the axes
    ax1.tick_params(axis='y', labelsize=ytick_fontsize)
    
    # Add a legend
    if legend:
        ax1.legend(handles=[plt.Line2D([0], [0], color=highlight_color, lw=4, marker='s', markersize=10, linestyle='')],
                labels=[f'Correlation > {mark_threshold}'],
                loc=legend_position, fontsize=legend_fontsize)
    
    # Top num_select drugs bar chart (using only the best drugs)
    top_drugs = drug_corrs.nlargest(num_select)
    top_colors = ['#C9C9C9' if x < mark_threshold else highlight_color for x in top_drugs]
    bars = ax2.bar(top_drugs.index, top_drugs.values, color=top_colors, edgecolor="none", linewidth=1, width=0.9)
    
    # Customize ax2
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.set_title(ax2_title, fontsize=title_fontsize, fontweight='bold')
    
    # Remove unnecessary spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    
    # Add text annotations to the top of the bars
    for bar in bars:
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.02,
            round(bar.get_height(), 3),
            horizontalalignment='center',
            color='#000000',
            weight='bold',
            fontsize=bar_annotation_fontsize,
            rotation="vertical"
        )
    
    # Add drug names below the bars
    for i, bar in enumerate(bars):
        # Determine position for drug names based on y-axis limits
        text_y_position = ax2_ylim[0] if ax2_ylim else 0.01
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            text_y_position + 0.02,
            top_drugs.index[i],
            horizontalalignment='center',
            color='#000000',
            fontsize=drug_name_fontsize,
            rotation="vertical",
        )
    
    ax2.tick_params(bottom=True, left=False, axis='x', which='major', pad=-1)
    
    plt.tight_layout()
    
    # Save or show the figure
    if output_path:
        plt.savefig(output_path, transparent=transparent_bg)
    if display_plot:
        plt.show()
    else:
        plt.close(fig)
    
    return fig, axes
