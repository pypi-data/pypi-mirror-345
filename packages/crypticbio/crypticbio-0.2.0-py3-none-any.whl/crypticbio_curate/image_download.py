


import os
import requests

def image_download(dataset, output_dir="images", max_images=None):
    """
    Downloads images and adds 'image_id' column. Uses filtered dataset length for filename padding.
    """
    max_images = int(max_images) if max_images is not None else None
    os.makedirs(output_dir, exist_ok=True)
    
    dataset = dataset.select(range(min(len(dataset), max_images))) if max_images else dataset

    url_column="url"

    def download_and_add_image_id(example, idx):
        #filename = os.path.join(output_dir, f"{idx:0{pad_width}d}.jpg")
        
        filename = os.path.join(output_dir, f"{idx}.jpg")
        try:
            if not os.path.exists(filename):  # avoid re-downloading
                response = requests.get(example[url_column], timeout=10)
                response.raise_for_status()
                with open(filename, "wb") as f:
                    f.write(response.content)
            example["image_id"] = filename
        except Exception as e:
            print(f"Failed to download {example[url_column]}: {e}")
            example["image_id"] = None
        return example

    dataset = dataset.map(download_and_add_image_id, with_indices=True)
    return dataset
