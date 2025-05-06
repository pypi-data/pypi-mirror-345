# CrypticBio: A Large Multimodal Dataset for Visually Confusing Biodiversity
We present [CrypticBio](https://huggingface.co/datasets/gmanolache/CrypticBio), the largest publicly available multimodal dataset of visually confusing species groups, specifically curated to support the development of AI models in the context of biodiversity identification applications. Visually confusing or cryptic species are groups of two or more taxa that are nearly indistinguishable based on visual characteristics alone. We open source-data the data pipeline, CrypticBio-Curate, which allows for custom subsets curation.


## Data Preprocessing
Before using this script, download the [metadata](https://huggingface.co/datasets/gmanolache/CrypticBio) from the Hugging Face repo.

## Models

We evaluate state-of-the-art CLIP-style models trained on biodiversity data using the scientific and vernacular terminology of species. We use [BioCLIP](https://huggingface.co/imageomics/bioclip); [BioTrove-CLIP](https://huggingface.co/BGLab/BioTrove-CLIP)'s BioCLIP ViT-B-16 and OpenAI ViT-B-16 fine-tuned variants; and [TaxaBind](https://huggingface.co/MVRL/taxabind-vit-b-16) as image-only baseline models. For multimodal learning, we add embeddings obtained from the image encoders to those obtained from TaxaBind location and environmental features encoders, which are then used for zero-shot classification. We collect from [WorldClim-2.1](https://www.worldclim.org/data/worldclim21.html) environmental features for each observation based on the location metadata, which are then passed through TaxaBind's environmental encoder. We benchmark on all English available vernacular terminology, and we use species scientific term when the vernacular terminology is missing.

| Name | Model URL |
| --- | --- | 
| BioCLIP | [https://github.com/kim2429/AmazonParrots/tree/main/Images](https://huggingface.co/imageomics/bioclip) | 
| BioTrove-CLIP | [https://huggingface.co/BGLab/BioTrove-CLIP](https://huggingface.co/BGLab/BioTrove-CLIP) | 
| TaxaBind | [https://huggingface.co/MVRL/taxabind-vit-b-16](https://huggingface.co/MVRL/taxabind-vit-b-16) | 

## Existing Benchmarks

We report results on the following established benchmarks from prior scientific literature: [Amazon Parrots](https://github.com/kim2429/AmazonParrots/tree/main/Images), [Chiroptera Rhinolophidae Rhinolophus](https://zenodo.org/records/10613387), and [Squamata Lacertidae Podarcis](https://tinyurl.com/Podarcis-images). We also introduce four new benchmarks: CrytpitcBio-Common, CrypticBio-CommonUnseen, CrytpicBio-Endangered, and CrytpicBio-Invasive, avaiable in the [Hugging Face repo](https://huggingface.co/datasets/gmanolache/CrypticBio/tree/main).

Our package expects a valid path to each image to exist in its corresponding metadata file; therefore, metadata CSV paths must be updated before running each benchmark.

| Name | Original Source | Metadata | Images |
| --- | --- | --- | --- |
| Amazon Parrots | [https://github.com/kim2429/AmazonParrots/tree/main/Images](https://github.com/kim2429/AmazonParrots/tree/main/Images) | exisitng_benchmarks/AmazonParrots.csv |  |
| Chiroptera Rhinolophidae Rhinolophus | [https://zenodo.org/records/10613387](https://zenodo.org/records/10613387) | exisitng_benchmarks/ChiropteraRhinolophidaeRhinolophus.csv  |  |
| Squamata Lacertidae Podarcis | [https://tinyurl.com/ Podarcis-images](https://tinyurl.com/Podarcis-images) | exisitng_benchmarks/SquamataLacertidaePodarcis.csv |  |
| Bumble Bees | not publicly available | - | - |
| Confounding Species | not publicly available | - | - |
| Sea Turtles | not publicly available | - | - |

## Acknowledgments
Parts of this project page were adopted from the [Nerfies](https://nerfies.github.io/) page.

## Website License
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
