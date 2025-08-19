MATLAB GUI
=============

.. note::

    Interactive GUI - please run each section individually. **DO NOT** run the entire script at once.

initial_alignment
--------------------
For loading path and image information:

- **Path setup** (first section): Users need to modify the paths to match their system
- **Image sizing**: It's recommended to resize images first:
  - **800 × 1140** pixels for coronal view
  - **1320 × 800** pixels for sagittal view
- If using original size images, specify ``use_already_downsampled_image=false`` in ``slice_preprocessing.m`` and ensure ``my_Resolution`` is set correctly




slice_preprocessing
-------------------
Image preprocessing pipeline including:

- Cropping and rotation
- Contrast adjustment  
- Downsampling of histology images



slice_registration
------------------
Slice registration to Allen Brain Atlas

.. tip::

    **Interactive Registration Workflow:**
    
    * **Setting transform points**: Press ``t`` in both slice and atlas viewer windows to label transformation points (minimum 10 points recommended)
    * **View results**: Press ``h`` + ``a`` to see the registration overlay
    * **Load existing transforms**: Press ``l`` to load transformation matrix
    
    **After each image:**
    
    * Press ``d`` to delete all points in both windows
    * Press ``h`` to leave overlay of current slice in atlas window  
    * Press ``→`` (right arrow) in slice window for next image
    * Press ``↓`` (down arrow), then scroll to find corresponding atlas position
    * Label new transformation points for the current image
    
    **Applying existing transformation matrices:**
    
    * Copy the .mat transformation file to the appropriate directory
    * Press ``l`` to load, then ``x`` to save the transformed image
    * Verify result using ``h`` + ``a``


save_transform_mat
------------------
Save the 3×3 transformation matrix for batch processing


analysis_rois
-------------
Analyze pixel-wise ROI locations and extract spatial coordinates within the Allen Brain Atlas coordinate system