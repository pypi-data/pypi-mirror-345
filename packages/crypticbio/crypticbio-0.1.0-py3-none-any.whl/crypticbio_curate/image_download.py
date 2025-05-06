# import os
# import requests
# from tqdm import tqdm
# from datasets import Dataset

# def image_download(dataset, url_column="url", output_dir="images", max_images=None):
#     """
#     Downloads images from a dataset's URL column.
#     """
#     os.makedirs(output_dir, exist_ok=True)

#     num_rows = dataset.num_rows
    
#     for i, item in tqdm(enumerate(dataset), total=num_rows):
#         if max_images and i >= max_images:
#             break

#         url = item[url_column]
#         filename = os.path.join(output_dir, f"{i:0{num_rows}d}.jpg")

#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()
#             with open(filename, "wb") as f:
#                 f.write(response.content)
#         except Exception as e:
#             print(f"Failed to download {url}: {e}")

#         dataset[i]["image_id"] = filename
    
#     return dataset


# from datasets import Dataset

# def image_download(dataset, url_column="url", output_dir="images", max_images=None):
#     """
#     Downloads images from a dataset's URL column and adds 'image_id' column with local filenames.
#     Uses filtered dataset length to determine filename padding.
#     """
#     os.makedirs(output_dir, exist_ok=True)

#     num_rows = len(dataset)
#     pad_width = len(str(min(num_rows, max_images) - 1)) if max_images else len(str(num_rows - 1))

#     image_ids = []

#     for i, item in tqdm(enumerate(dataset), total=num_rows):
#         if max_images and i >= max_images:
#             break

#         url = item[url_column]
#         filename = os.path.join(output_dir, f"{i:0{pad_width}d}.jpg")

#         try:
#             response = requests.get(url, timeout=10)
#             response.raise_for_status()
#             with open(filename, "wb") as f:
#                 f.write(response.content)
#         except Exception as e:
#             print(f"Failed to download {url}: {e}")
#             filename = None

#         image_ids.append(filename)

#     # Pad image_ids list if max_images < num_rows
#     if max_images and max_images < num_rows:
#         image_ids += [None] * (num_rows - max_images)

#     dataset = dataset.add_column("image_id", image_ids)
#     return dataset


import os
import requests
from tqdm import tqdm

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
