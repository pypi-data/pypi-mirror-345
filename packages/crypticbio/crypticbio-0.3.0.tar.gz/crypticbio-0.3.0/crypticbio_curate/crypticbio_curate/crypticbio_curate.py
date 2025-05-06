
from .metadata_loader import load_metadata, filter_metadata, load_config, save_dataset
from .image_download import image_download

def main():
    config = load_config('config.yaml')

    # Step 1: Process metadata
    dataset = load_metadata(**config.get('dataset', {}))

    # Step 2: Filter metadata
    filtered = filter_metadata(dataset, **config.get('filters', {}))

    # Step 3: Download images
    filtered = image_download(filtered, **config.get('download', {}))

    # Step 4: Save paired metadata
    save_dataset(filtered, **config.get('generate_pairs', {}))
