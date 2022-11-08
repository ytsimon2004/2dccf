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

    YW001_reg/
        ├── resize/
        │    ├── processed/
        │    │   ├── YW001_g*_s*_processed.tif
        │    │   └── transformations/
        │    │       ├── labelled_regions/
        │    │       │   └── output.csv
        │    │       ├── transform_matrix/
        │    │       │   └── YW001_gx_sx_processed_transform_data.mat
        │    │       ├── YW001_g*_s*_processed_transform_data.mat
        │    │       └── YW001_g*_s*_processed_transformed.tif
        │    └── YW001_g*_s*_resize.tif
        ├── zproj/
        │    └── YW001_g*_s*_{channel}.tif
        ├── roi/
        │    └── YW001_g*_s*_{channel}.roi
        │ 
        └── output_files/ (for generate output fig)


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
   (scrolling for finding proper slice angle). Press `t` in both slice/altas viewer windows for labeling transform points (at least 10 points are recommended).
   Press `h` + `a` to see the result. For loading the transformation matrix, press `l`

4. `Analyze_ROIs.m`: quantification for ROIs in each channel, and output .mat/.csv 


## Contact
- Yu-Ting Wei (ytsimon2004@gmail.com)
