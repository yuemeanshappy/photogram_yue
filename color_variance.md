# Color variance

potential software:
1. image G
2. Blender
3. Slicer: https://besjournals.onlinelibrary.wiley.com/doi/10.1111/2041-210X.13669
4. Pixel Binning Method (R package): https://cran.r-project.org/web/packages/colordistance/vignettes/binning-methods.html
5. patternize (R package): https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/2041-210X.12853


**Pixel Binning Method**
- Binning is a way for grouping continuous data into categories defined by specific ranges so that we can know the proportion of each major color. 
- Plot pixels from a 2D image and categorize them
- can get the proportion of each color categorization


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
- output
  - heatmap to show the differences between images
  - PCA to group species based on pattern differences   
