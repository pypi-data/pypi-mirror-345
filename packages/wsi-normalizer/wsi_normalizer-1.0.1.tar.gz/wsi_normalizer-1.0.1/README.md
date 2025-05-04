# WSI Normalizer: a color stain normalization tool/package for whole slide images

![GitHub](https://github.com/HaoyuCui/WSI_Normalizer/)

Inspired by & reconstructed from this repository [link](https://github.com/wanghao14/Stain_Normalization)

How to start? [blog](https://blog.csdn.net/CalvinTri/article/details/135429053)

## Description
Repository for normalizing whole slide images (WSI) patches.

## Updates
**[04/2025]** We have upload the [PyPI package](https://pypi.org/project/wsi-normalizer/) for this repository. You can directly install it by using pip and use it without clone the repository.

### Support for:
1. [Reinhard](https://ieeexplore.ieee.org/abstract/document/946629/) Reinhard, Erik, et al. "Color transfer between images." IEEE Computer graphics and applications 21.5 (2001): 34-41.
2. [Macenko](https://ieeexplore.ieee.org/abstract/document/5193250) Macenko, Marc, et al. "A method for normalizing histology slides for quantitative analysis." 2009 IEEE international symposium on biomedical imaging: from nano to macro. IEEE, 2009.
3. [Vahadane](https://ieeexplore.ieee.org/abstract/document/7460968/) Vahadane, Abhishek, et al. "Structure-preserving color normalization and sparse stain separation for histological images." IEEE transactions on medical imaging 35.8 (2016): 1962-1971.

## Package Usage

Install the package via PyPI:

```bash
pip install wsi-normalizer
```

Then you can use it in your code:

```python
import cv2
from wsi_normalizer import imread, MacenkoNormalizer  # or ReinhardNormalizer, VahadaneNormalizer, TorchVahadaneNormalizer

macenko_normalizer = MacenkoNormalizer()
macenko_normalizer.fit(imread('TARGET_IMAGE.jpg'))
norm_img = macenko_normalizer.transform(imread('INPUT_IMAGE.jpg'))

cv2.imwrite('OUTPUT_IMAGE.jpg', cv2.cvtColor(norm_img, cv2.COLOR_RGB2BGR))
```