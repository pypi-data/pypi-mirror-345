import os
from datasets import load_dataset
import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_metadata(selected_data_file=None):
    """
    Loads the dataset metadata from Hugging Face.
    """
    return load_dataset("gmanolache/CrypticBio", split="train", data_files=selected_data_file, download_mode="force_redownload")

def apply_flexible_filter(dataset, column_name, value):
    if value is None:
        return dataset
    if isinstance(value, list):
        return dataset.filter(lambda x: x[column_name] in value)
    if isinstance(value, bool):
        return dataset.filter(lambda x: x[column_name] is not None)
    return dataset.filter(lambda x: x[column_name] == value)

def filter_metadata(
    dataset,
    speciesScientificName=None,
    kingdomTaxonomicGroup=None,
    classTaxonomicGroup=None,
    year=None,
    month=None,
    day=None,
    coordinates=None,
    hasVernacularName=None,
    hasCrypticGroup=None
):
    """
    Filters the dataset flexibly using exact values or lists of values.
    """
    dataset = apply_flexible_filter(dataset, "scientificName", speciesScientificName)
    dataset = apply_flexible_filter(dataset, "kingdom", kingdomTaxonomicGroup)
    dataset = apply_flexible_filter(dataset, "class", classTaxonomicGroup)
    dataset = apply_flexible_filter(dataset, "year", year)
    dataset = apply_flexible_filter(dataset, "month", month)
    dataset = apply_flexible_filter(dataset, "day", day)
    dataset = apply_flexible_filter(dataset, "coordinates", coordinates)
    dataset = apply_flexible_filter(dataset, "vernacularName", hasVernacularName)
    dataset = apply_flexible_filter(dataset, "crypticGroup", hasCrypticGroup)
    
    return dataset

def save_dataset(dataset, output_dir="metadata"):
    """
    Generates pairs of metadata and sequences.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Convert to pandas DataFrame
    df = dataset.to_pandas()

    df.to_csv(os.path.join(output_dir, "metadata.csv"), index=False)

    
