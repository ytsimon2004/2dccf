2dccf
======

* Tools for do the 2d mouse brain registration
* adapted from [allenCCF](https://github.com/cortex-lab/allenCCF)


## Project structure
    2dccf/
        ├── archive/ 
        ├── fiji/ (ijm script)
        ├── ref/ (for atlas references files)
        └── src/
            ├── npy-matlab/
            ├── util/
            ├── util_allenccf/
            ├── Initiate_AllignTools.m
            ├── Process_Histology.m
            ├── Navigate_Atlas_and_Register_Slices.m
            └── Analyze_ROIs.m

## Data structure
# TODO reference
    YW001_reg/
        ├── raw/ (optional) -- (1)
        │
        ├── zproj/ -- (2)
        │    └── YW001_g*_s*_{channel}.tif
        │
        ├── roi/ -- (3)
        │    └── YW001_g*_s*_{channel}.roi  
        │
        ├── roi_cpose/ -- (3')
        │    └── YW001_g*_s*_{channel}.roi          
        │
        ├── resize/ (src for the allenccf) 
        │    ├── YW001_g*_s*_resize.tif -- (4)
        │    │ 
        │    └── processed/
        │           ├── YW001_g*_s*_resize_processed.tif -- (5)
        │           └── transformations/
        │                 ├── YW001_g*_s*_resize_processed_transformed.tif -- (6)
        │                 │
        │                 ├── YW001_g*_s*_resize_processed_transform_data.mat -- (7)
        │                 │
        │                 │ 
        │                 └── labelled_regions/
        │                       ├── {*channel}_roitable.csv -- (8) 
        │                       └── parsed_data / 
        │                             └── parsed_csv_merge.csv -- (9)
        │
        ├── resize_overlap/* (optional) -- (10)
        └── output_files/ (for generate output fig or analysis)

* (1). raw data for confocal (i.e., .lsm, .czi or .tiff)
* (2). z projection stacks, should be `RGB` format and save per channel (r, g, b and o)
* (3). roi file after imageJ selection
* (3'). roi file using cellpose pipeline (dev)
* (4). merged ROI, scaled RGB tif file for registration. normally use **blue (DAPI)** channel as a reference.
  for example, **green roi + red roi + DAPI channel**. Since limited channel numbers, overlap channel need to save to
  another file using pseudo-color, then used the same transformation matrix to do the registration procedure
* (5) contrast or rotated image after process
* (6) image after transformation
* (7) transformation matrix for each slices
* (8) allenccf output (per ROI)
* (9) csv after parsed and classification (used for data visualization)
* (10) if there is overlap channel, create the same folder structure as r/g channels. ** Note that use the same transformation matrix

# How to start?
## Preprocess using fiji
1. use Fiji/ImageJ to count the cells (i.e., `multipointer`), and save as .roi file
2. merge the roi files and DAPI based tif file, flatten the images and reshape. 
3. To reshape the images, normally 1140(ML)*800(DV) for coronal slice, 1320(AP)*800(DV).

## Download reference files
1. download the [reference npy](http://data.cortexlab.net/allenCCF/), then put into the project `ref` folder

## Run 
1. `Initiate_AllignTools.m`: load path (tif file under the resize folder) and images info

2. `Process_Histology.m`: adjust the contrast of individual slices and rotation, 
keyboard shortcut can be found in `HistologyHotkeyFcn` in `HistologyBrowser.m`\
   (`c` for selecting channel, `s` for save, `r` for rollback, `space` for adjusting contrast ...)

3. `Navigate_Atlas_and_Register_Slices.m`: slice registration (tilt slice angle). check keyboard shortcut in command window
   (scrolling for finding proper slice angle).

4. `Analyze_ROIs.m`: quantification for ROIs in each channel, and output .mat/.csv 


## User Tips for Transformation GUI
* For batch images, Press `t` in both slice/altas viewer windows for labeling transform points 
(at least 10 points are recommended). Press `h` + `a` to see the result. For loading the transformation matrix, press `l` 
* After each image 
  * Press `d` to delete all the points for both windows 
  * Press `h` for leaving the overlay the current slice in atlas windows
  * Press &rarr; (right arrow key) in slice windows for the next image
  * Press &darr; (down arrow key), then scroll down for the corresponding in atlas windows
  * Label transformation points for the new image

* if need to apply the existing batch transformation matrices
  * copy the matrices .mat file
  * Press `l`, and `x` for saving the transformed image file (verify using `h` + `a`)



## Contact
- Yu-Ting Wei (ytsimon2004@gmail.com)
