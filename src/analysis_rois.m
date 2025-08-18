%% Analyze Regions of Interest (ROIs)
% This script extracts ROI coordinates and anatomical annotations from 
% registered histological slices. It generates tables containing the spatial
% location and brain region identity of each detected ROI.
%
% Output: ROI tables with AP/DV/ML coordinates and anatomical annotations

%% Data Folder Configuration
path2data = [processed_images_folder, '\transformations'];
data = dir(fullfile(path2data, '*_data.mat'));
images = dir(fullfile(path2data, '*transformed.tif'));
annotation_volume_location = [path2ref, '\annotation_volume_10um_by_index.npy'];
structure_tree_location = [path2ref, '\structure_tree_safe_2017.csv'];
save_folder = [path2data, '\labelled_regions'];

%% Process Each Transformed Image
listTable = cell(length(images), n_ch);
clc;

for i = 1:length(images)
    image_name = images(i).name;
    tmp = regexp(image_name, '_');
    fprintf('Processing image %d of %d\n', i, length(images));
    
    % File paths for current image and transformation data
    full_image_name = fullfile(path2data, image_name);
    data_name = data(i).name;
    full_data_name = fullfile(path2data, data_name);
    
    % Load transformed slice image and transformation data
    transformed_slice_image = imread(full_image_name);
    transform_data = load(full_data_name);
    transform_data = transform_data.save_transform;
    
    % Extract transformation parameters
    slice_to_atlas_transform = transform_data.transform;
    slice_num = transform_data.allen_location{1};   % Atlas slice position
    slice_angle = transform_data.allen_location{2}; % Slice angle
    
    % Load ROI image data
    rois = imread(full_image_name);
    
    % Extract color channels for ROI detection
    [roi_r, roi_g, ~] = imsplit(rois);  % Red, Green, Blue channels
    
    % Process ROI channels using regional maxima
    % This ensures one-to-one mapping between original and transformed ROIs
    % for non-contiguous ROI pixels (e.g., individual neurons)
    rois_r = uint8(imregionalmax(roi_r));
    [d1, d2] = size(rois_r);
    rois_g = uint8(imregionalmax(roi_g));
    
    % Handle cases where channels have no ROIs
    if sum(roi_r(:)) == 0 && sum(roi_g(:)) == 0
        rois_r = uint8(zeros(d1, d2));
        rois_g = uint8(zeros(d1, d2));
    elseif sum(roi_r(:)) == 0
        rois_r = uint8(zeros(d1, d2));
    elseif sum(roi_g(:)) == 0
        rois_g = uint8(zeros(d1, d2));
    end
    
    % Load reference brain annotations (if not already loaded)
    if ~exist('av', 'var') || ~exist('st', 'var')
        disp('Loading reference atlas...');
        av = readNPY(annotation_volume_location);
        st = loadStructureTree(structure_tree_location);
    end
    
    % Configure annotation volume for the selected viewing plane
    if strcmp(plane, 'coronal')
        av_plot = av;
    elseif strcmp(plane, 'sagittal')
        av_plot = permute(av, [3 2 1]);
    elseif strcmp(plane, 'transverse')
        av_plot = permute(av, [2 3 1]);
    end
    
    % Organize ROI channels for processing
    rois_total = {rois_r; rois_g};
    
    % Process each color channel for ROI analysis
    for channel = n_rgb
        clear roi_annotation;
        rois_cur = rois_total{channel};
        
        % Validate ROI image dimensions (should match atlas reference size)
        assert(size(rois_cur, 1) == 800 && size(rois_cur, 2) == 1140 && size(rois_cur, 3) == 1, ...
               'ROI image dimensions do not match expected atlas size');
        
        % Initialize coordinate and annotation arrays
        num_rois = sum(rois_cur(:) > 0);
        full_image_name = zeros(num_rois, 3);  % [AP, DV, ML] coordinates
        roi_annotation = cell(num_rois, 3);    % [annotation_ID, name, acronym]
        
        % Find ROI pixel locations
        [pixels_row, pixels_column] = find(rois_cur > 0);
        
        % Atlas coordinate system parameters
        bregma = allenCCFbregma();          % Bregma position in reference space
        atlas_resolution = 0.010;          % Atlas resolution in mm
        ref_size = size(squeeze(av_plot(1, :, :)));
        offset_map = get_offset_map(slice_angle, ref_size);
        
        % Convert each ROI pixel to atlas coordinates and anatomical annotation
        for pixel = 1:length(pixels_row)
            
            % Calculate offset due to slice angle (compensates for non-orthogonal cuts)
            offset = offset_map(pixels_row(pixel), pixels_column(pixel));
            
            % Convert pixel coordinates to stereotactic coordinates (AP/DV/ML)
            % Coordinates are relative to bregma in millimeters
            if strcmp(plane, 'coronal')
                ap = -(slice_num - bregma(1) + offset) * atlas_resolution;  % Anterior-Posterior
                dv = (pixels_row(pixel) - bregma(2)) * atlas_resolution;   % Dorsal-Ventral
                ml = (pixels_column(pixel) - bregma(3)) * atlas_resolution; % Medial-Lateral
            elseif strcmp(plane, 'sagittal')
                ml = -(slice_num - bregma(3) + offset) * atlas_resolution;
                dv = (pixels_row(pixel) - bregma(2)) * atlas_resolution;
                ap = -(pixels_column(pixel) - bregma(1)) * atlas_resolution;
            elseif strcmp(plane, 'transverse')
                dv = -(slice_num - bregma(2) + offset) * atlas_resolution;
                ml = (pixels_row(pixel) - bregma(3)) * atlas_resolution;
                ap = -(pixels_column(pixel) - bregma(1)) * atlas_resolution;
            end
            
            % Store stereotactic coordinates
            full_image_name(pixel, :) = [ap, dv, ml];
            
            % Get anatomical annotation for this ROI pixel
            ann = av_plot(slice_num + offset, pixels_row(pixel), pixels_column(pixel));
            name = st.safe_name{ann};   % Full anatomical region name
            acr = st.acronym{ann};      % Anatomical region acronym
            
            % Store annotation data
            roi_annotation{pixel, 1} = ann;  % Annotation index
            roi_annotation{pixel, 2} = name; % Region name
            roi_annotation{pixel, 3} = acr;  % Region acronym
            
        end
        % Create ROI results table for current channel
        roi_table = table(roi_annotation(:, 2), roi_annotation(:, 3), ...
                         full_image_name(:, 1), full_image_name(:, 2), full_image_name(:, 3), ...
                         roi_annotation(:, 1), ...
                         'VariableNames', {'name', 'acronym', 'AP_location', 'DV_location', ...
                                          'ML_location', 'avIndex'});
        listTable{i, channel} = roi_table;
    end
end

%% Consolidate and Save Results
% Combine results from all images for each channel
rois_name = {'rfp'; 'gfp'};

for ch = n_rgb
    Coordinates = table();
    rois_name_cur = rois_name{ch};
    
    % Concatenate all ROI tables for current channel
    for i = 1:size(listTable, 1)
        tables = listTable{i, ch};
        Coordinates = [Coordinates; tables];
    end
    
    % Create output directory if needed
    if ~exist(save_folder, 'dir')
        mkdir(save_folder);
    end
    
    % Generate output filenames
    filename = [image_name(1:tmp(1)-1), '_', rois_name_cur, '_roitable.mat'];
    csvfile = [image_name(1:tmp(1)-1), '_', rois_name_cur, '_roitable.csv'];
    
    % Save results in both MATLAB and CSV formats
    save(fullfile(save_folder, filename), 'Coordinates');
    writetable(Coordinates, fullfile(save_folder, csvfile));
end

% Display completion message
A = load(fullfile(save_folder, [image_name(1:tmp(1)-1), '_', rois_name_cur, '_roitable.mat']));
disp('=== ROI Analysis Complete ===');
disp('Output files saved in labelled_regions folder:');
disp('- .mat files for MATLAB analysis');
disp('- .csv files for external analysis');
disp('=============================');
