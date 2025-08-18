%% Save Transform Matrix from Allen CCF Registration
% This script loads Allen CCF transform matrices and extracts the 3x3 
% transformation matrix for use with external tools.
%
% Background: scipy.io cannot correctly parse MATLAB's projective2d output,
% so we extract and save the raw transformation matrix separately.
%
% Created: 2022-03-28 by Yu-Ting
% Modified for improved documentation and formatting

% Define paths
path2data = [processed_images_folder, '\transformations'];
transform_mat = dir(fullfile(path2data, '*transform_data*.mat'));
save_folder = [path2data, '\transform_matrix'];

% Create output directory if it doesn't exist
if ~exist(save_folder, 'dir')
    mkdir(save_folder);
end

% Process each transformation file
for i = 1:length(transform_mat)
    mat_name = transform_mat(i).name;
    
    % Load transformation matrix from the saved data
    t = load(fullfile(path2data, mat_name)).save_transform.transform.T;
    
    % Validate matrix dimensions
    assert(all(size(t) == [3,3]), ...
           'Transform matrix is not the correct 3x3 shape');
    
    % Save the extracted transformation matrix
    output_filename = transform_mat(i).name;
    save(fullfile(save_folder, output_filename), 't');
    
    fprintf('>>> Saved %s transformation matrix\n', output_filename);
end
