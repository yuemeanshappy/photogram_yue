# Color variance

potential software:
1. Pixel Binning Method (R package): https://cran.r-project.org/web/packages/colordistance/vignettes/binning-methods.html
2. patternize (R package): https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12853


**Pixel Binning Method**
- Binning is a way for grouping continuous data into categories defined by specific ranges so that we can know the proportion of each major color. 
- Plot pixels from a 2D image and categorize them
- **can get the proportion of each color categorization**


**patternize: 2D image alignment and color categorization**
- 2D image alignment
  - landmark based:\
    1)[affine](https://blog.csdn.net/u011681952/article/details/98942207)(unifrom changes);\
    2)[TPS](https://khanhha.github.io/posts/Thin-Plate-Splines-Warping/), thin plate spline (non-unifrom changes) 
  - image registration: LTS, least trimmed square
- color categorization
  - RGB threshold
  - k-means clustering
  - watershed transformation
- **output**
  - heatmap to show the differences between images
  - PCA to group species based on pattern differences   


<div class="sketchfab-embed-wrapper"> <iframe title="P. batangensis" frameborder="0" allowfullscreen mozallowfullscreen="true" webkitallowfullscreen="true" allow="autoplay; fullscreen; xr-spatial-tracking" xr-spatial-tracking execution-while-out-of-viewport execution-while-not-rendered web-share src="https://sketchfab.com/models/c17c921d18384e319fed5eca664a4aea/embed"> </iframe> <p style="font-size: 13px; font-weight: normal; margin: 5px; color: #4A4A4A;"> <a href="https://sketchfab.com/3d-models/p-batangensis-c17c921d18384e319fed5eca664a4aea?utm_medium=embed&utm_campaign=share-popup&utm_content=c17c921d18384e319fed5eca664a4aea" target="_blank" style="font-weight: bold; color: #1CAAD9;"> P. batangensis </a> by <a href="https://sketchfab.com/yuemeanshappy?utm_medium=embed&utm_campaign=share-popup&utm_content=c17c921d18384e319fed5eca664a4aea" target="_blank" style="font-weight: bold; color: #1CAAD9;"> yuemeanshappy </a> on <a href="https://sketchfab.com?utm_medium=embed&utm_campaign=share-popup&utm_content=c17c921d18384e319fed5eca664a4aea" target="_blank" style="font-weight: bold; color: #1CAAD9;">Sketchfab</a></p></div>
