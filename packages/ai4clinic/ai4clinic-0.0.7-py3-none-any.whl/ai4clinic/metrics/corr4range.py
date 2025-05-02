import torch
from torch import Tensor
from torchmetrics.functional import pearson_corrcoef, spearman_corrcoef

def corr4range(predictions: Tensor,
                          labels: Tensor,
                          threshold: float,
                          sensitive_area: str = "bottom",
                          corr_type: str = "spearman") -> Tensor:
    """
    Calculate the correlation between predictions and labels within a sensitive area.

    The sensitive area is defined by a threshold on the labels:
      - If sensitive_area is "bottom", only data points with labels < threshold are used.
      - If sensitive_area is "top", only data points with labels > threshold are used.

    The correlation is computed using precomputed functions from the torchmetrics package:
      - Pearson correlation is computed via `torchmetrics.functional.pearson_corrcoef`.
      - Spearman correlation is computed via `torchmetrics.functional.spearman_corrcoef`.

    Parameters
    ----------
    predictions : torch.Tensor
        A 1D tensor of predicted values.
    labels : torch.Tensor
        A 1D tensor of actual label values.
    threshold : float
        The threshold value to define the sensitive area.
    sensitive_area : str, optional
        Indicates whether the sensitive area is at the "bottom" (labels < threshold) or
        "top" (labels > threshold) of the label distribution. Default is "bottom".
    corr_type : str, optional
        The type of correlation to compute. Options are "pearson" or "spearman".
        Default is "spearman".

    Returns
    -------
    torch.Tensor
        A scalar tensor representing the computed correlation. If no data points fall within
        the specified sensitive area, returns NaN.
    """
    # Select indices based on the specified sensitive area.
    if sensitive_area.lower() == "bottom":
        indices = (labels < threshold).nonzero(as_tuple=True)[0]
    elif sensitive_area.lower() == "top":
        indices = (labels > threshold).nonzero(as_tuple=True)[0]
    else:
        raise ValueError("sensitive_area must be either 'bottom' or 'top'.")

    if indices.numel() == 0:
        return torch.tensor(float('nan'))

    sensitive_predictions = predictions[indices]
    sensitive_labels = labels[indices]

    # Compute the requested correlation using torchmetrics functions.
    if corr_type.lower() == "pearson":
        return pearson_corrcoef(sensitive_predictions, sensitive_labels)
    elif corr_type.lower() == "spearman":
        return spearman_corrcoef(sensitive_predictions, sensitive_labels)
    else:
        raise ValueError("corr_type must be either 'pearson' or 'spearman'.")

