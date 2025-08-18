%% Process Histology Images
% This script performs comprehensive histology image processing including:
% - Cropping, rotation, and contrast adjustment
% - Image downsampling to match atlas resolution
% - Quality control and orientation correction
%
% IMPORTANT: Run each section individually, not the entire script at once

%% Set File and Parameters
% Display current configuration information
clc;
fprintf('=== Image Processing Configuration ===\n');
disp(['TIF files location: ', path2image]);
disp(['Resolution: ', num2str(my_Resolution), ' pixels per µm']);
disp(['Section plane: ', myPlane]);
disp(['ROI channels: ', name_rgb]);
fprintf('======================================\n');

% Directory structure configuration
image_folder = path2image;  % Source directory for histology images

% Directory to save processed images (can be same as image_folder)
% Results will be stored in a 'processed' subfolder
save_folder = image_folder;

% Image file discovery and ordering
% Images should be ordered anterior to posterior (or vice versa)
% Processed images will be named: [original_name]_processed.tif
image_file_names = dir([image_folder filesep '*.tif']);
image_file_names = natsortfiles({image_file_names.name});
% Alternative: manually specify image order
% image_file_names = {'slide_no_2_RGB.tif', 'slide_no_3_RGB.tif', 'slide_no_4_RGB.tif'};

% Image type configuration
% Set to true if images are individual slices
% Set to false if images contain multiple slices requiring cropping
image_files_are_individual_slices = true;

% Resolution configuration
% Set to true if images are already at atlas resolution (10µm/pixel)
% Set to false if downsampling is required
use_already_downsampled_image = true;
 

% Pixel size parameters
% microns_per_pixel: resolution of input images (used only if downsampling needed)
% microns_per_pixel_after_downsampling: target resolution to match atlas (typically 10µm)
microns_per_pixel = 1/my_Resolution; 
microns_per_pixel_after_downsampling = 10;

% Additional processing parameters
% save_file_name: prefix for cropped slices (if processing multi-slice images)
% Example: 3rd slice from 2nd image -> save_folder/processed/save_file_name02_003.tif
% save_file_name = 'SS096_';

% Image enhancement
gain = 1;  % Increase if images need brightness adjustment

% Atlas reference dimensions
% Standard sizes: [800 1320] for sagittal, [800 1140] for coronal
atlas_reference_size = my_atlas_ref;

% Create output directory structure
folder_processed_images = fullfile(save_folder, 'processed');
if ~exist(folder_processed_images, 'dir')
    mkdir(folder_processed_images);
end

%% LOAD AND PROCESS SLICE PLATE IMAGES

% close all figures
close all
   

% if the images need to be downsampled to 10um pixels (use_already_downsampled_image = false), 
% this will downsample and allow you to adjust contrast of each channel of each image from image_file_names
%
% if the images are already do
% wnsampled (use_already_downsampled_image = true), this will allow
% you to adjust the contrast of each channel 
%
% Open Histology Viewer figure
try figure(histology_figure);
catch; histology_figure = figure('Name' ,'Histology Viewer'); end
warning('off', 'images:initSize:adjustingMag'); warning('off', 'MATLAB:colon:nonIntegerIndex');

% mfunction to downsample and adjust histology image
HistologyBrowser(histology_figure, save_folder, image_folder, image_file_names, folder_processed_images, image_files_are_individual_slices, ...
            use_already_downsampled_image, microns_per_pixel, microns_per_pixel_after_downsampling, gain)


%% CROP AND SAVE SLICES -- run once the above is done, if image_file_are_individual_slices = false

% close all figures
close all

% run this function if the images from image_file_names have several
% slices, per image (e.g. an image of an entire histology slide)
%
% this function allows you to crop all the slices you would like to 
% process im each image, by drawing rectangles around them in the figure. 
% these will be further processed in the next cell
% if ~image_files_are_individual_slices
    %histology_figure = figure('Name','Histology Viewer');
    %HistologyCropper(histology_figure, save_folder, image_file_names, atlas_reference_size, save_file_name, use_already_downsampled_image)
%else
    %disp('individually cropped slices already available')
%end


%% GO THROUGH TO FLIP HORIZONTAL SLICE ORIENTATION, ROTATE, SHARPEN, and CHANGE ORDER

% close all figures
close all
            
% this takes images from folder_processed_images ([save_folder/processed]),
% and allows you to rotate, flip, sharpen, crop, and switch their order, so they
% are in anterior->posterior or posterior->anterior order, and aesthetically pleasing
% 
% it also pads images smaller than the reference_size and requests that you
% crop images larger than this size
% note -- presssing left or right arrow saves the modified image, so be
% sure to do this even after modifying the last slice in the folder
slice_figure = figure('Name','Slice Viewer');
SliceFlipper(slice_figure, folder_processed_images, atlas_reference_size)


