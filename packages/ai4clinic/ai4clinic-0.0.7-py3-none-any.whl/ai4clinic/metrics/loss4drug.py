import torch
from torch import Tensor
from typing import Callable, Union

def loss4drug(criterion: Union[Callable[[Tensor, Tensor], Tensor], str],
                  drugs_ids: Union[Tensor, list, 'np.ndarray'],
                  predictions: Union[Tensor, list, 'np.ndarray'],
                  labels: Union[Tensor, list, 'np.ndarray']) -> Tensor:
    """
    Calculate the loss per unique drug and return the average loss.

    This function groups predictions and labels by drug ID, computes the loss for each group
    using the provided criterion, and returns the average loss across all unique drugs.
    The inputs can be provided as PyTorch tensors, NumPy arrays, or Python lists.

    Parameters
    ----------
    criterion : callable or str
        Either a loss function that takes two tensors (predictions and labels) and returns a scalar loss,
        or a string specifying the desired loss method. Supported strings include:
            - "mse", "mse_loss", or "mean_squared_error": Uses torch.nn.MSELoss(reduction='mean').
            - "l1", "l1_loss", or "mean_absolute_error": Uses torch.nn.L1Loss(reduction='mean').
    drugs_ids : Tensor, list, or np.ndarray
        A 1D array-like structure containing drug IDs corresponding to each prediction-label pair.
    predictions : Tensor, list, or np.ndarray
        A 1D array-like structure containing predicted values.
    labels : Tensor, list, or np.ndarray
        A 1D array-like structure containing actual label values.

    Returns
    -------
    torch.Tensor
        A scalar tensor representing the average loss across unique drugs.
    """
    # Convert inputs to torch.Tensor if they are not already.
    if not isinstance(drugs_ids, torch.Tensor):
        drugs_ids = torch.as_tensor(drugs_ids)
    if not isinstance(predictions, torch.Tensor):
        predictions = torch.as_tensor(predictions)
    if not isinstance(labels, torch.Tensor):
        labels = torch.as_tensor(labels)

    # Initialize the loss function if a string is provided.
    if not callable(criterion):
        if isinstance(criterion, str):
            criterion_name = criterion.lower()
            if criterion_name in ("mse", "mse_loss", "mean_squared_error"):
                criterion = torch.nn.MSELoss(reduction='mean')
            elif criterion_name in ("l1", "l1_loss", "mean_absolute_error"):
                criterion = torch.nn.L1Loss(reduction='mean')
            else:
                raise ValueError(f"Unsupported loss type string: {criterion}")
        else:
            raise ValueError("criterion must be a callable or a valid loss type string.")

    total_loss = 0.0
    unique_drugs = torch.unique(drugs_ids)

    # Iterate over each unique drug and compute the loss for that group.
    for drug_id in unique_drugs:
        # Get the indices for the current drug.
        indices = (drugs_ids == drug_id).nonzero(as_tuple=True)[0]
        # Gather predictions and labels corresponding to these indices.
        grouped_predictions = predictions[indices]
        grouped_labels = labels[indices]
        # Compute the loss for the current group.
        current_loss = criterion(grouped_predictions, grouped_labels)
        total_loss += current_loss

    # Average the loss over the number of unique drugs.
    average_loss = total_loss / unique_drugs.numel()
    return average_loss