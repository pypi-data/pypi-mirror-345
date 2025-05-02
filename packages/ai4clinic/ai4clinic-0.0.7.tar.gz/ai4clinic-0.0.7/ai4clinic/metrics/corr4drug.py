import torch
from torch import Tensor
from torchmetrics.functional import pearson_corrcoef, spearman_corrcoef
from typing import Union

def corr4drug(drugs_ids: Union[Tensor, list, 'np.ndarray'],
                  predictions: Union[Tensor, list, 'np.ndarray'],
                  labels: Union[Tensor, list, 'np.ndarray'],
                  corr_type: str = "spearman") -> float:
    """
    Calculate the correlation per unique drug and return the average correlation.

    This function groups predictions and labels by drug ID, computes the correlation for each group
    using the specified correlation method (Pearson or Spearman), and returns the average correlation
    across all drug groups that have at least two data points.

    Parameters
    ----------
    drugs_ids : torch.Tensor, list, or np.ndarray
        A 1D array-like structure containing drug IDs for each prediction-label pair.
    predictions : torch.Tensor, list, or np.ndarray
        A 1D array-like structure containing predicted values.
    labels : torch.Tensor, list, or np.ndarray
        A 1D array-like structure containing actual label values.
    corr_type : str, optional
        The type of correlation to compute. Options are "pearson" or "spearman".
        Default is "spearman".

    Returns
    -------
    float
        The average correlation across all unique drugs. If no valid drug groups exist,
        returns NaN.
    """
    # Convert inputs to torch.Tensor if they aren't already.
    if not isinstance(drugs_ids, torch.Tensor):
        drugs_ids = torch.as_tensor(drugs_ids)
    if not isinstance(predictions, torch.Tensor):
        predictions = torch.as_tensor(predictions)
    if not isinstance(labels, torch.Tensor):
        labels = torch.as_tensor(labels)

    total_corr = 0.0
    valid_drug_count = 0
    unique_drugs = torch.unique(drugs_ids)
    
    for drug_id in unique_drugs:
        # Get indices for the current drug.
        indices = (drugs_ids == drug_id).nonzero(as_tuple=True)[0]
        grouped_predictions = predictions[indices]
        grouped_labels = labels[indices]
        
        # Skip drug groups with fewer than 2 data points (correlation is undefined).
        if grouped_predictions.numel() < 2:
            continue

        # Compute the chosen correlation.
        if corr_type.lower() == "pearson":
            corr_value = pearson_corrcoef(grouped_predictions, grouped_labels)
        elif corr_type.lower() == "spearman":
            corr_value = spearman_corrcoef(grouped_predictions, grouped_labels)
        else:
            raise ValueError("corr_type must be either 'pearson' or 'spearman'.")

        # Replace any NaN values with 0.
        corr_value = torch.nan_to_num(corr_value, nan=0.0)
        
        # Optionally print the drug ID if the correlation is nonzero.
        if corr_value != 0:
            print(f"Drug ID {drug_id.item()} has correlation {corr_value.item():.4f}")
        
        total_corr += float(corr_value)
        valid_drug_count += 1

    if valid_drug_count == 0:
        return float('nan')
    return total_corr / valid_drug_count

