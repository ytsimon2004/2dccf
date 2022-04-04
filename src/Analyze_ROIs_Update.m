%% Folders for the data (adjust if necessary)
path2data = [processed_images_folder, '\transformations'];
data = dir(fullfile(path2data,'*_data.mat'));
images = dir (fullfile(path2data, '*transformed.tif'));
annotation_volume_location = [pata2ref,'\annotation_volume_10um_by_index.npy'];
structure_tree_location = [pata2ref,'\structure_tree_safe_2017.csv'];
save_folder= [path2data, '\labelled regions'];

%% LOAD THE DATA
listTable = cell(length(images),n_ch);clc
for i = 1:length(images)
    image_name = images(i).name;
    tmp = regexp(image_name,'_');
    disp([num2str(i), ' of ', num2str(length(images))]);%image_name(1:tmp(4)-1)]
    full_image_name = fullfile(path2data, image_name);
    data_name= data(i).name;
    full_data_name = fullfile(path2data, data_name);
    
    % load the transformed slice image
    transformed_slice_image = imread(full_image_name);
    % load the transform from the transform file
    transform_data = load(full_data_name);
    transform_data = transform_data.save_transform;
    
    % get the actual transformation from slice to atlas
    slice_to_atlas_transform = transform_data.transform;
    
    % get the position within the atlas data of the transformed slice
    slice_num = transform_data.allen_location{1};
    slice_angle = transform_data.allen_location{2};
    
    % load the rois
    rois = imread(full_image_name);
    
    %extract red chqnnel aka your roi
    [roi_r, roi_g, B]= imsplit(rois);
    
    % if the rois come from a transformed roi image of non-contiguous roi
    % pixels (e.g. an ROI pixel for each neuron), then run this line to ensure
    % a one-to-one mapping between ROIs in the original and transformed images:
    
    %     % if the rois come from a transformed roi image of non-contiguous roi
    %     % pixels (e.g. an ROI pixel for each neuron), then run this line to ensure
    %     % a one-to-one mapping between ROIs in the
    %     %original and transformed images:
    rois_r = uint8(imregionalmax(roi_r));[d1 d2] = size(rois_r);
    rois_g = uint8(imregionalmax(roi_g));
    %
    if sum(sum(roi_r)) == 0 && sum(sum(roi_g)) == 0
        rois_r = uint8(zeros(d1,d2));
        rois_g = uint8(zeros(d1,d2));
    elseif sum(sum(roi_r)) == 0
        rois_r = uint8(zeros(d1,d2));
    elseif sum(sum(roi_g)) == 0
        rois_g = uint8(zeros(d1,d2));
    else
    end
    
    % load the reference brain annotations
    if ~exist('av','var') || ~exist('st','var')
        disp('loading reference atlas...')
        av = readNPY(annotation_volume_location);
        st = loadStructureTree(structure_tree_location);
    end
    
    % select the plane for the viewer
    if strcmp(plane,'coronal')
        av_plot = av;
    elseif strcmp(plane,'sagittal')
        av_plot = permute(av,[3 2 1]);
    elseif strcmp(plane,'transverse')
        av_plot = permute(av,[2 3 1]);
    end
    
    rois_total = {rois_r;rois_g};
    
    for channel = n_rgb
        clear roi_annotation
        rois_cur = []; rois_cur = rois_total{channel};
        assert(size(rois_cur,1)== 800&size(rois_cur,2)==1140&size(rois_cur,3)==1,'roi image is not the right size');
        full_image_name = zeros(sum(rois_cur(:)>0),3);
        roi_annotation = cell(sum(rois_cur(:)>0),3);
        % get location and annotation for every roi pixel
        [pixels_row, pixels_column] = find(rois_cur>0);
        
        % generate other necessary values
        bregma = allenCCFbregma(); % bregma position in reference data space
        
        atlas_resolution = 0.010; % mm
        ref_size = size(squeeze(av_plot(1,:,:)));
        offset_map = get_offset_map(slice_angle, ref_size);
        
        % loop through every pixel to get ROI locations and region annotations
        for pixel = 1:length(pixels_row)
            
            % get the offset from the AP value at the centre of the slice, due to
            % off-from-coronal angling
            offset = offset_map(pixels_row(pixel),pixels_column(pixel));
            
            % use this and the slice number to get the AP, DV, and ML coordinates
            if strcmp(plane,'coronal')
                ap = -(slice_num-bregma(1)+offset)*atlas_resolution;
                dv = (pixels_row(pixel)-bregma(2))*atlas_resolution;
                ml = (pixels_column(pixel)-bregma(3))*atlas_resolution;
            elseif strcmp(plane,'sagittal')
                ml = -(slice_num-bregma(3)+offset)*atlas_resolution;
                dv = (pixels_row(pixel)-bregma(2))*atlas_resolution;
                ap = -(pixels_column(pixel)-bregma(1))*atlas_resolution;
            elseif strcmp(plane,'transverse')
                dv = -(slice_num-bregma(2)+offset)*atlas_resolution;
                ml = (pixels_row(pixel)-bregma(3))*atlas_resolution;
                ap = -(pixels_column(pixel)-bregma(1))*atlas_resolution;
            end
            
            full_image_name(pixel,:) = [ap dv ml];
            
            % finally, find the annotation, name, and acronym of the current ROI pixel
            ann = av_plot(slice_num+offset,pixels_row(pixel),pixels_column(pixel));
            name = st.safe_name{ann};
            acr = st.acronym{ann};
            
            roi_annotation{pixel,1} = ann;
            roi_annotation{pixel,2} = name;
            roi_annotation{pixel,3} = acr;
            
        end
        roi_table = []; roi_table = table(roi_annotation(:,2),roi_annotation(:,3), ...
            full_image_name(:,1),full_image_name(:,2),full_image_name(:,3), roi_annotation(:,1), ...
            'VariableNames', {'name', 'acronym', 'AP_location', 'DV_location', 'ML_location', 'avIndex'});
        listTable{i,channel} = roi_table;
        %save(fullfile(save_folder,[image_name(1:25),'_',rois_name_cur,'_roitable.mat']),'roi_table')
    end
end
% Save the tables as one big table
rois_name = {'rfp';'gfp'};
Coordinates= table();
for ch = n_rgb
    rois_name_cur = rois_name{ch};
    for i = 1:size(listTable,1)
        tables = listTable{i,ch};
        Coordinates = [Coordinates; tables];
    end
    
    if ~exist(save_folder)
    mkdir(save_folder)
    end
    
    save(fullfile(save_folder,[image_name(1:tmp(2)-1),'_',rois_name_cur,'_roitable.mat']), 'Coordinates');
end
A = load(fullfile(save_folder,[image_name(1:tmp(2)-1),'_',rois_name_cur,'_roitable.mat']));
disp(['Finished: ', 'Check variable A'])
