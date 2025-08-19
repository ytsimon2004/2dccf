%% Initiate Allen CCF Tools
% This script initializes the Allen Common Coordinate Framework (CCF) tools
% for histological image registration and analysis.

% Set up paths - modify this to match your local installation
if ispc
    homeDir = fullfile(getenv('HOMEDRIVE'), getenv('HOMEPATH')); % Windows
else
    homeDir = getenv('HOME'); % Linux / macOS
end

path2code = [homeDir '\code\ccf2d\matlab']
addpath(genpath([path2code]));
path2ccf = [path2code '\allenccf'];
path2ref = [homeDir '\.ccf2d'];

% Check if CCF reference data exists
if ~exist(path2ref, 'dir')
    error(['CCF reference data not found at: ' path2ref newline ...
           'Please run "ccf2d init" in your terminal first to download the required atlas data.']);
end

% Choose your image folder with the tif files
path2image = uigetdir('E:\data\user\yu-ting\');

%% Image Resolution Setup
% Check Fiji -> Image -> Show Info... -> Resolution 
% Common values: 0.4216, 0.8431 pixels per µm (used for downsampling)
my_Resolution = input('What is the resolution (pixels per µm)? ');

%% Atlas Reference Size Configuration
clc;
inputSag = input('Which section type are you using? (sagittal: press 1, coronal: press 0): ');
if inputSag == 1 || isempty(inputSag)  % Sagittal section
    my_atlas_ref = [800 1320];
    myPlane = 'sagittal';
else  % Coronal section
    my_atlas_ref = [800 1140]; 
    myPlane = 'coronal';
end

%% Channel Information Configuration
clc;
fprintf('Channel options:\n');
fprintf('1: RFP (ROI detection)\n');
fprintf('2: GFP (ROI detection)\n');
fprintf('3: GFP + RFP (dual channel ROI detection)\n');
myChannel = input('Please select channel configuration (1-3): ');

if myChannel == 1 
    n_ch = 1;
    n_rgb = 1;
    name_rgb = 'red';
elseif myChannel == 2
    n_ch = 1;
    n_rgb = 2;
    name_rgb = 'green';
else
    myChannel = 2;
    n_ch = 2;
    n_rgb = [1 2];
    name_rgb = 'red + green';
end

%% Step 1: Preprocess the Images
% This script performs image preprocessing including:
% - Cropping and rotation
% - Contrast adjustment
% - Downsampling of histology images
% 
% Instructions: Run each section sequentially
% (First section -> Second Section -> Last section)
slice_preprocessing

%% Step 2: Register Slices to Allen Brain Atlas 
% This script handles the registration of histological slices
% to the Allen Common Coordinate Framework
slice_registration

%% Step 3: Analyze Regions of Interest (ROIs)
% Extract ROI table with spatial locations of selected cells
% throughout the entire brain coordinate system
analysis_rois


