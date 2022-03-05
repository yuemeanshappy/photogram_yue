# photogram_myself
Detailed Notes about how to do photogrammetry with command line based open source software.

## Overview
**1. color calibration:** apply color profile to all raw images

**2. image sorting:** sort images based on angle and rotation

**3. focus stacking:** merge multiple images of the same angle and rotation into a single image

**4. establish model**\
**a. build mask:** mask the background so that the background would not interrupt the image alignment process

**b. align photos:** align photos according to the camera positions

**c. build mesh:** build the structure/skeleton of the object

**d. build texture:** add color and texture to the physical structure

**e. scale model based on marks**

## Preparation
- A colorful color checker and a black/white color checker for color calibration\
In this example, we use X-Rite ColorChecker Passport Photo 2 as the color checker

- A set of photos from different angles, rotations and focus distances\
Here, we use *Pedicularis cranolopha* as an example. We took images from three angles (top-down, horizontal and bottom-up), roughly 60 rotations per angel and around 5 images per rotation to cover the whole focus distances.

## I. Color calibration
Apply the same color checker (color profile) to all images.

**1. software**: Adobe Lightroom Classic (paid)\
(Python pacakges: OpenCV and PlantCV) not successful at this point
```bash
conda install opencv
````
**2. usage**\
**(1) download Xrite Color Checker Camera Calibration software and Adobe DNG converter software**

**(2) create color profile**\
  a. open Adobe lightroom, click on `File` > `Plug-in Manager` > `add`
  
  b. navigate to `Library` > `Application Support` > `Adobe` > `Lightroom` > `Modules` > `XRiteColorCameraCalibration.Irplugin` > `Add Plug-in`
  
  c. click on the color chart, then `File` > `Export with preset` > Choose `Xrite presets` from the drop down menu
  
  d. name the profile and `export`
  
**(3) apply color profile to all images and export color calibrated images**\
  a. open Adobe Lightroom, select `Development`
  
  b. select the first photo, and choose the color profile created in the last step in 'Basic` > `profile`
  
  c. select all photos and click `synchronize`, choose color calibration only
  
  d. select all photos and click `File` > `Export`
  
Notes:\
Adobe Lightroom is relatively user friendly. ~800 photos takes ~0.5 hours. However, there is no command line version of this software, and it can become very repetitive if we have more than ten sets of photos to deal with (with 10 times of clicks and waiting for the results)

<img src="/images/right is after calibration.png" width="300">
Before(left) and After(right) color calibration

## II. Cluster photos by angles and rotations
Refer to python scripts (cluster_photos_by_time_intervals.py)

## III. Focus stacking
We used Helicon Focus to do the focus stacking (command lines)\
The user guide of [Helicon Focus](https://www.heliconsoft.com/focus/help/english/HeliconFocus.html) 
The output format of the file could be `dng` or `jpeg`.
```bash
# ~/HeliconFocus is the install location on the mac
/Applications/HeliconFocus.app/Contents/MacOS/HeliconFocus -silent /path/to/the/input/files -save:/path/to/the/output/files -mp:1 -rp:8 -sp:4
mp: method
rp: radius
sp: smoothing
````
For batch processing in command lines, refer to python scripts(helicon_focus.py)

## IV. Establish model
### 4.1 remove background of images (build masks on the background)
There are two ways to remove background of images. The first one is to use batch process in Adobe Photoshop to fill the object in white color and fill the background with black color. This method works pretty well for single image, but will usually fail (cannot capture the flower) in batch process. 

The second method requires images of the same size and the same resolution, so we need to use Photoshop to resize the images (dimensions: 5400 * 3600, resolution: 1520 * 1520, why? because the raw file has the similar size of dimensions and the same resolution )and set the output file format as tiff. 
IMPORTANT: need to choose the correct profile when open the dng file in Camera raw and use this and embed profile when save image.\
<img src="/images/photoshop.png" width="500" height="300">
<img src="/images/photoshop_profile_choice.png" width="500" height="300">

The color profile in red square should be the same

**1. check the dimensions and resolutions of image (.dng)**\
```bash
pip3 install PyExifTool
````
```python
import exiftool

with exiftool.ExifTool() as et:
    metadata = et.get_metadata('/path/to/RAW.DNG')

print(metadata)
````
**2. use Photoshop to resize the image and set the output file format as tiff**

**(1) Create actions to batch process images**\
a. Click `actions` > `create new actions` > name the action (e.g. resize) > `begin recording `

b. `image size` > fill `fit to` with the drop down menu `custom` > set the width and height `dimensions` and set the unit as `pixels` > set the `resolution`           > set the `resample` as `automatic`

c. `save` images as `tiff` in a new file directionary or within the same directionary\
 **(2) Batch process images**\
       Click `File` > `Automate` > `Batch` > select the input file source and output file source > `OK`

**3. Use Agisoft Metashape to build mask**\
     a. select anyone of the output images and fill it with black in Photoshop (`Select all` > `Fill` > `Black`) and name it as background.tiff
     
     b. open agisoft metashape and add all images that we are going to use
     
     c. select one of the image and `File` > `Import` > `Import mask`
     
     d. select `method` as `background`, `operation` as `replacement`, set the tolerance value between 40-60, click `apply to selected image`
     
     e. check the mask created in the photo panel
     
     f. if it works, then use the same setting in step d and apply it to all images. if it does not work, then reset the tolerance value\
  (the final version of the mask would be: the object is in white and the background is in black, black part is the masked part and would not participate in photo alignment)
 
### 4.2 align photos

**1. align photos**\
Go to `Workflow` > click `align photos` > put the `accuracy` on `high` > in the section `Advanced`, do **NOT** check Generic preselection(since the function will align photos firstly in low accuracy to cut down the time, when we do not select this function, the images can be correctly aligned and the time is not significantly increased) > select `Apply masks to key points` > click OK.

**2. alignment ajustment**\
  a. `Model` > `Gradual selection` > `reconstruction uncertainty` > set the threshold value as 10 (the larger the number, the worst the alignment will be) > delete selected points
  
  b. Go to the `reference` panel > click `optimize camera` button > select all cameras except the last two > click OK (this will adjust the position of all cameras based on certain algorithum)
  
  c. `Model` > `Gradual selection` > `project accuracy` > set the threshold value as 10 (the larger the number, the worst the alignment will be) > delete selected points
  
  d. `Model` > `Gradual selection` > `reprojection error` > et the threshold value as 1 > delete selected points
  
  e. use seleciton tool and manually delete points

Notes:\
For 134 images, there would be 20 min for photo alignments. (Mask building can significantly improve the alignment speed! Otherwise, might need 1 hour to align photos with background)

### 4.3 build mesh
Go to `workflow` > click `build mesh` > set `source data` as `depth maps` > set `quality` and `face count` as `high` > in the advanced section, select `calculate vertex color` > click  `ok`\
(We can smooth the mesh although I think there is no significant difference before/after smoothing process. Also, we can fill holes by `Tools`>`Mesh`>`close holes`. If the hole is too large, there is another way as said in the manual that we need to build dense cloud between photo alignment and mesh building, and set one of the parameter as certain value so that the software will automatically build a mesh without holes)

Notes:\
For 134 images, there would be roughly 50min to build the mesh. (Mask building can significantly improve the alignment speed! Otherwise, might need 16 hours to build the mesh. crazy!!)

### 4.4 build texture
Go to `workflow` > click `build texture` > use the default setting and click ok
  
### 4.5 LAST STEP! scale the model based on the markers
Randomly choose three images. Clik the image > Add markers on the start and end side of the ruler > Select the markers (e.g. point1 and point2, point3 and point4, point5 and point6) in the marker panel at the same time > add scale bar > set the distance between two markers > `update tranform`
