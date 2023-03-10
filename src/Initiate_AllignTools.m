%% Initiate Allen CCF Tools
path2code = 'E:\data\user\yu-ting\repo\2dccf';
addpath(genpath([path2code]));
cd([path2code,'\src']);
path2CCF = [path2code '\src\util_allenccf'];
pata2ref = [path2code '\ref'];
% chooose your image folder with the tif files
path2image = uigetdir('E:\data\user\yu-ting\');

%% put your image resolution
% check Fiji-> Show Info0... -> Resolution 
% 0.4216 
% 0.8431
my_Resolution = input('what is the resolution (pixels per um)?');

%% add atlas_reference_size
clc;inputSag = input('which section are used? (sagittal press 1, coronal press 0)');
if inputSag == 1 || isempty(inputSag)%Saggital section
    my_atlas_ref = [800 1320];
    myPlane = 'sagittal';
else
    my_atlas_ref = [800 1140]; 
    myPlane = 'coronal';
end

%% Channel information 
clc;
myChannel = input('please put channel information: \n1:rfp(roi); 2:gfp(roi); 3:gfp(roi)+ rfp(roi)');
if myChannel == 1 
    n_ch = 1;n_rgb = 1;name_rgb = 'red';
elseif myChannel == 2
    n_ch = 1;n_rgb = 2;name_rgb = 'green';
else
    myChannel = 2;
    n_ch = 2;
    n_rgb = [1 2];name_rgb = 'red + green';
end

%% Step1: Preproces the images
% Open and run the following script 
% To Crop, Rotate, Adjust Contrast, and Downsample Histology
% Follow the instruction and run each section at one time: 
% First section -> Second Section -> Last section 
Process_Histology

%% Step2: Register your slice to the allen brain atlas 
% Run the following script 
Navigate_Atlas_and_Register_Slices

%% Step3: Register your slice to the allen brain atlas 
% To extract a roi table with the locations of every selected cell in the entire brain
Analyze_ROIs


