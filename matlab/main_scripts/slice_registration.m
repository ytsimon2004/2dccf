%% Navigate Atlas and Register Slices
% This script launches the Allen Atlas Browser for interactive registration
% of histological slices to the Allen Common Coordinate Framework (CCF).
%
% Workflow:
% 1. Load reference atlas data (annotation, structure tree, template)
% 2. Configure viewing plane and file locations  
% 3. Launch interactive atlas and slice browsers
% 4. Perform manual registration of histology to atlas coordinates

%% File Locations and Configuration

% Directory containing processed histology images
processed_images_folder = [image_folder filesep 'processed'];

% Probe save name suffix (prevents overwriting existing probe sets)
probe_save_name_suffix = ''; 

% Reference atlas file locations
annotation_volume_location = [path2ref, '\annotation_volume_10um_by_index.npy'];
structure_tree_location = [path2ref, '\structure_tree_safe_2017.csv'];
template_volume_location = [path2ref, '\template_volume_10um.npy'];

% Viewing plane configuration ('coronal', 'sagittal', 'transverse')
plane = myPlane;

%% Load Reference Atlas Data

% Load reference brain volumes and region annotations
if ~exist('av','var') || ~exist('st','var') || ~exist('tv','var')
    disp('Loading reference atlas data...');
    av = readNPY(annotation_volume_location);      % Annotation volume
    st = loadStructureTree(structure_tree_location); % Structure tree  
    tv = readNPY(template_volume_location);        % Template volume
end

% Configure viewing plane orientation
if strcmp(plane, 'coronal')
    av_plot = av;
    tv_plot = tv;
elseif strcmp(plane, 'sagittal')
    av_plot = permute(av, [3 2 1]);
    tv_plot = permute(tv, [3 2 1]);
elseif strcmp(plane, 'transverse')
    av_plot = permute(av, [2 3 1]);
    tv_plot = permute(tv, [2 3 1]);
end

%% Launch Interactive Atlas Registration Interface

% Create main Atlas Viewer figure
f = figure('Name', 'Atlas Viewer'); 

% Initialize or reuse Slice Viewer figure for histology display
try 
    figure(slice_figure_browser); 
    title('');
catch
    slice_figure_browser = figure('Name', 'Slice Viewer'); 
end

% Configure reference dimensions and launch slice browser
reference_size = size(tv_plot);
sliceBrowser(slice_figure_browser, processed_images_folder, f, reference_size);

% Launch Atlas Transform Browser (full version with slice interface)
% This provides interactive registration between histology and atlas
[f] = AtlasTransformBrowser(f, tv_plot, av_plot, st, slice_figure_browser, ...
                           processed_images_folder, probe_save_name_suffix); 

% Alternative: Simple atlas browser without slice interface
% Uncomment the following lines to use the simplified version:
% 
% save_location = processed_images_folder;
% f = allenAtlasBrowser(tv_plot, av_plot, st, save_location, probe_save_name_suffix);