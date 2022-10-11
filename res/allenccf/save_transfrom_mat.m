%% load the allenCCF transform mat, and extract and save the transform matrix (3,3)
%% Due to scipy.io cannot correctly parse the projective2d output
%% 220328 created by yu-ting

path2data = [processed_images_folder, '\transformations'];
transform_mat = dir(fullfile(path2data, '*transform_data*.mat'));
save_folder = [path2data, '\transform_matrix'];

if ~exist(save_folder)
mkdir(save_folder)
end

for i = 1:length(transform_mat);
    mat_name = transform_mat(i).name;
    t = load(fullfile(path2data, mat_name)).save_transform.transform.T;
    assert(all(size(t) == [3,3]), 'transform matrix is not the right shape');
    o = transform_mat(i).name;
    save(fullfile(save_folder, o), 't');
    disp(['>>> save ',o,'transform matrix'])
end
