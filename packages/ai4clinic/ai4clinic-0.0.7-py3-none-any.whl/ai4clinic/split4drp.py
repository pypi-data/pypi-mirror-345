import os
import numpy as np
import pandas as pd
import shutil
from typing import Union, List
from rich.console import Console
from rich.table import Table

def split4drp(
    patients: Union[List, np.ndarray, pd.Series],
    drugs: Union[List, np.ndarray, pd.Series],
    response: Union[List, np.ndarray, pd.Series],
    split_type: str,
    output_path: str,
    cancer_type: Union[List, np.ndarray, pd.Series] = None,
    folds: int = 5,
    seed: int = 42,
    val_proportion: float = 0.2,
    print_table: bool = True
) -> None:
    """
    Splits the drug response prediction dataset into cross-validation folds 
    based on the specified strategy.

    Parameters
    ----------
    patients : array-like
        List of patient/cells ID/name for each sample.
    drugs : array-like
        List of drug identifiers or feature representations.
    response : array-like
        List of drug response values.
    cancer_type : array-like
        List of cancer type identifiers corresponding to each sample.
    split_type : str
        Strategy for splitting the dataset. Options are 'random', 'patient-blind', 
        'drug-blind', 'completely-blind', 'cancer-blind'.
    output_path : str
        Path where the generated dataset splits will be saved.
    folds : int, default=5
        Number of folds for cross-validation.
    seed : int, default=42
        Random seed for reproducibility.
    val_proportion : float, default=0.2
        Fraction of training data used for validation.
    print_table : bool, default=True
        Whether to print a summary table of the datasets.

    Returns
    -------
    None
        The function saves the split datasets to disk.
    """
    
    # Convert inputs to Pandas DataFrame or list
    if isinstance(patients, pd.Series):
        patients = patients.tolist()
    if isinstance(drugs, pd.Series):
        drugs = drugs.tolist()
    if isinstance(response, pd.Series):
        response = response.tolist()
    if cancer_type is not None and isinstance(cancer_type, pd.Series):
        cancer_type = cancer_type.tolist()

    if cancer_type is not None:
        if not (len(patients) == len(drugs) == len(response) == len(cancer_type)):
            print("Error: The lengths of the input lists (patients, drugs, response, cancer_type) are not the same.")
            return
    elif not (len(patients) == len(drugs) == len(response)):
        print("Error: The lengths of the input lists (patients, drugs, response) are not the same.")
        return

    if split_type == 'cancer-blind':
        if cancer_type is None:
            print("Error: 'cancer-blind' split type requires cancer_type to be provided.")
            return

    np.random.seed(seed)

    # Create the DataFrame .
    if cancer_type is not None:
        data = pd.DataFrame({
            'patient': patients,
            'drug': drugs,
            'response': response,
            'cancer': cancer_type
        })
    else:
        data = pd.DataFrame({
            'patient': patients,
            'drug': drugs,
            'response': response
        })
    
    # Create a shuffled version of the data (used for saving all samples)
    shuffled_data = data.sample(frac=1, random_state=seed)

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # -------------------------------------------------------------------
    def split_train_validate_proportional(train_data: pd.DataFrame, col: str, num_val_groups: int):
        """
        Splits the training data into new training and validation sets proportionally,
        grouping by the specified column.
        """
        counts = train_data[col].value_counts()
        items = list(counts.to_dict().items())  
        np.random.shuffle(items)  
        total = sum(freq for _, freq in items)
        target = round(total / num_val_groups)
        groups = {}
        current_group = 0
        cumulative = 0
        for val, freq in items:
            groups[val] = current_group
            cumulative += freq
            if cumulative >= (current_group + 1) * target and current_group < num_val_groups - 1:
                current_group += 1
        val_values = [val for val, grp in groups.items() if grp == 0]
        new_train = train_data[~train_data[col].isin(val_values)]
        validate = train_data[train_data[col].isin(val_values)]
        return new_train, validate
    # -------------------------------------------------------------------
    def split_train_validate_random(train_data: pd.DataFrame, proportion: float):
        """
        Splits training data into new training and validation sets using the specified proportion.
        """
        train_shuffled = train_data.sample(frac=1, random_state=seed)
        n_val = int(len(train_shuffled) * proportion)
        validate = train_shuffled.iloc[:n_val]
        new_train = train_shuffled.iloc[n_val:]
        return new_train, validate
    # -------------------------------------------------------------------
    def assign_groups_by_freq(data: pd.DataFrame, col: str, num_folds: int) -> list:
        """
        Assigns unique values in the specified column to num_folds groups, 
        aiming to balance the total number of samples in each fold.
        """
        freq = data[col].value_counts()
        unique_vals = list(freq.index)
        np.random.shuffle(unique_vals)
        total_samples = data.shape[0]
        target = total_samples / num_folds
        fold_groups = [[] for _ in range(num_folds)]
        cumulative = 0
        fold_index = 0
        for val in unique_vals:
            fold_groups[fold_index].append(val)
            cumulative += freq[val]
            if cumulative >= (fold_index + 1) * target and fold_index < num_folds - 1:
                fold_index += 1
        return fold_groups
    # -------------------------------------------------------------------
    def save_and_summarize_datasets(train: pd.DataFrame, test: pd.DataFrame, validate: pd.DataFrame, output_path: str, fold_number: int, seed: int, print_table: bool, cancer_type: pd.DataFrame):
        """
        Summarizes the unique patients, drugs, and cancer types in the train, test, and validate datasets,
        and saves the datasets to disk.
        """
        train_patient_count = train['patient'].nunique()
        train_drug_count = train['drug'].nunique()

        test_patient_count = test['patient'].nunique()
        test_drug_count = test['drug'].nunique()

        validate_patient_count = validate['patient'].nunique()
        validate_drug_count = validate['drug'].nunique()
        
        if cancer_type is not None:
            train_cancer_count = train['cancer'].nunique()
            test_cancer_count = test['cancer'].nunique()
            validate_cancer_count = validate['cancer'].nunique()

        # Calculate unique overlapping patients and drugs
        overlap_train_test_patient = pd.Series(train['patient'].unique()).isin(test['patient'].unique()).sum()
        overlap_train_test_drug = pd.Series(train['drug'].unique()).isin(test['drug'].unique()).sum()

        overlap_train_val_patient = pd.Series(train['patient'].unique()).isin(validate['patient'].unique()).sum()
        overlap_train_val_drug = pd.Series(train['drug'].unique()).isin(validate['drug'].unique()).sum()

        overlap_test_val_patient = pd.Series(test['patient'].unique()).isin(validate['patient'].unique()).sum()
        overlap_test_val_drug = pd.Series(test['drug'].unique()).isin(validate['drug'].unique()).sum()

        # Create a rich table with a random color based on the fold number
        colors = ["bold red", "bold green", "bold blue", "bold yellow", "bold magenta", "bold cyan"]
        color_index = hash(fold_number) % len(colors)
        header_color = colors[color_index]

        if print_table:
            console = Console()
            table = Table(show_header=True, header_style=header_color)
            table.add_column("Set", style="dim", width=12)
            table.add_column("Patient #", justify="right")
            table.add_column("Drug #", justify="right")
            table.add_column("Cancer Type #", justify="right")
            table.add_column("Overlap Train-Test (Patients)", justify="right")
            table.add_column("Overlap Train-Test (Drugs)", justify="right")
            table.add_column("Overlap Train-Val (Patients)", justify="right")
            table.add_column("Overlap Train-Val (Drugs)", justify="right")
            table.add_column("Overlap Test-Val (Patients)", justify="right")
            table.add_column("Overlap Test-Val (Drugs)", justify="right")

            table.add_row(
                "Train",
                str(train_patient_count),
                str(train_drug_count),
                str(train_cancer_count) if cancer_type is not None else "-",
                str(overlap_train_test_patient),
                str(overlap_train_test_drug),
                str(overlap_train_val_patient),
                str(overlap_train_val_drug),
                "-",
                "-"
            )
            table.add_row(
                "Test",
                str(test_patient_count),
                str(test_drug_count),
                str(test_cancer_count) if cancer_type is not None else "-",
                "-",
                "-",
                str(overlap_train_val_patient),
                str(overlap_train_val_drug),
                str(overlap_test_val_patient),
                str(overlap_test_val_drug)
            )
            table.add_row(
                "Validate",
                str(validate_patient_count),
                str(validate_drug_count),
                str(validate_cancer_count) if cancer_type is not None else "-",
                "-",
                "-",
                "-",
                "-",
                str(overlap_test_val_patient),
                str(overlap_test_val_drug)
            )

            console.print(table)

        # Create fold folder and save files
        fold_folder = os.path.join(output_path, f"samples{str(fold_number)}")
        if not os.path.exists(fold_folder):
            os.makedirs(fold_folder)

        train.sample(frac=1, random_state=seed).to_csv(
            os.path.join(fold_folder, "train.txt"), sep='\t', header=False, index=False)
        test.sample(frac=1, random_state=seed).to_csv(
            os.path.join(fold_folder, "test.txt"), sep='\t', header=False, index=False)
        validate.sample(frac=1, random_state=seed).to_csv(
            os.path.join(fold_folder, "validate.txt"), sep='\t', header=False, index=False)
    # -------------------------------------------------------------------
    def save_all_samples(all_data: pd.DataFrame, output_path: str, seed: int):
        """
        Saves all samples to the specified output path.
        """
        all_samples_folder = os.path.join(output_path, "allsamples")
        if not os.path.exists(all_samples_folder):
            os.makedirs(all_samples_folder)
        all_data.sample(frac=1, random_state=seed).to_csv(
            os.path.join(all_samples_folder, "train.txt"), sep='\t', header=False, index=False)
        all_data.sample(frac=1, random_state=seed).to_csv(
            os.path.join(all_samples_folder, "test.txt"), sep='\t', header=False, index=False)
        all_data.sample(frac=1, random_state=seed).to_csv(
            os.path.join(all_samples_folder, "validate.txt"), sep='\t', header=False, index=False)
    # -------------------------------------------------------------------
    if split_type == 'random':
        # Random split: shuffle the entire dataset and divide into folds.
        shuffled_data = data.sample(frac=1, random_state=seed).reset_index(drop=True)
        groups = np.array_split(shuffled_data, folds)

        for i in range(folds):
            print(f"Creating fold number: {i+1}")
            test = groups[i]
            train_data = pd.concat([groups[j] for j in range(folds) if j != i])
            new_train, validate = split_train_validate_random(train_data, proportion=val_proportion)
            save_and_summarize_datasets(new_train, test, validate, output_path, i+1, seed, print_table,cancer_type)
            save_all_samples(shuffled_data, output_path, seed)

    elif split_type == 'cell-blind':
        # Cell-blind: all samples from the same patient remain together.
        fold_groups = assign_groups_by_freq(data, 'patient', folds)
        num_val_groups = int(round(1 / val_proportion))
        for i in range(folds):
            print(f"Creating fold number: {i+1}")
            test = data[data['patient'].isin(fold_groups[i])]
            train_data = data[~data['patient'].isin(fold_groups[i])]
            new_train, validate = split_train_validate_proportional(train_data, 'patient', num_val_groups)
            save_and_summarize_datasets(new_train, test, validate, output_path, i+1, seed, print_table,cancer_type)
            save_all_samples(shuffled_data, output_path, seed)

    elif split_type == 'drug-blind':
        # Drug-blind: all samples from the same drug remain together.
        fold_groups = assign_groups_by_freq(data, 'drug', folds)
        num_val_groups = int(round(1 / val_proportion))
        for i in range(folds):
            print(f"Creating fold number: {i+1}")
            test = data[data['drug'].isin(fold_groups[i])]
            train_data = data[~data['drug'].isin(fold_groups[i])]
            new_train, validate = split_train_validate_proportional(train_data, 'drug', num_val_groups)
            save_and_summarize_datasets(new_train, test, validate, output_path, i+1, seed, print_table,cancer_type)
            save_all_samples(shuffled_data, output_path, seed)

    elif split_type == 'completely-blind':
        # Completely-blind: ensure that neither patients nor drugs in the test set appear in training.
        patient_groups = assign_groups_by_freq(data, 'patient', folds)
        drug_groups = assign_groups_by_freq(data, 'drug', folds)
        num_val_groups = int(round(1 / val_proportion))
        for i in range(folds):
            print(f"Creating fold number: {i+1}")
            test = data[(data['patient'].isin(patient_groups[i])) & (data['drug'].isin(drug_groups[i]))]
            train_data = data[~(data['patient'].isin(patient_groups[i]) | data['drug'].isin(drug_groups[i]))]
            new_train, validate = split_train_validate_proportional(train_data, 'patient', num_val_groups)
            save_and_summarize_datasets(new_train, test, validate, output_path, i+1, seed, print_table,cancer_type)
            save_all_samples(shuffled_data, output_path, seed)

    elif split_type == 'cancer-blind':
        # Cancer-blind: all samples from the same cancer type remain together.
        fold_groups = assign_groups_by_freq(data, 'cancer', folds)
        num_val_groups = int(round(1 / val_proportion))
        for i in range(folds):
            print(f"Creating fold number: {i+1}")
            test = data[data['cancer'].isin(fold_groups[i])]
            train_data = data[~data['cancer'].isin(fold_groups[i])]
            new_train, validate = split_train_validate_proportional(train_data, 'cancer', num_val_groups)
            save_and_summarize_datasets(new_train, test, validate, output_path, i+1, seed, print_table,cancer_type)
            save_all_samples(shuffled_data, output_path, seed)
    
    else:
        print("Unsupported split_type. Options are: 'random', 'cell-blind', 'drug-blind', 'completely-blind', 'cancer-blind'.")
        return