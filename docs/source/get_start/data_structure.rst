Data Directory Structure
=============================
For batch processing (i.e., whole brain / multiple channels processing)


.. code-block:: text

    YW001_reg/
        ├── raw/ (optional) -- (1)
        │
        ├── zproj/ -- (2)
        │    └── YW001_g*_s*_{channel}.tif
        │
        ├── roi/ -- (3)
        │    └── YW001_g*_s*_{channel}.roi
        │
        ├── roi_cpose/ -- (3')
        │    └── YW001_g*_s*_{channel}.roi
        │
        ├── resize/ (src for the allenccf)
        │    ├── YW001_g*_s*_resize.tif -- (4)
        │    │
        │    └── processed/
        │           ├── YW001_g*_s*_resize_processed.tif -- (5)
        │           └── transformations/
        │                 ├── YW001_g*_s*_resize_processed_transformed.tif -- (6)
        │                 │
        │                 ├── YW001_g*_s*_resize_processed_transform_data.mat -- (7)
        │                 │
        │                 └── labelled_regions/
        │                       ├── {*channel}_roitable.csv -- (8)
        │                       └── parsed_data/
        │                             └── parsed_csv_merge.csv -- (9)
        │
        ├── resize_overlap/* (optional) -- (10)
        └── output_files/ (for generated figures or analysis outputs)

Placeholders
------------

- ``g*`` : Index of glass slide.
- ``s*`` : Index of Slice .
- ``{channel}`` : Channel name (e.g., ``r``, ``g``, ``b``, ``o(overlap)``).

Reference (1)–(10)
------------------

1. **raw/** — Raw confocal data (e.g., ``.lsm``, ``.czi``, or ``.tiff``). *(optional)*
2. **zproj/** — Z-projection stacks. Must be **RGB** and saved **per channel** (``r``, ``g``, ``b``, ``o``).
3. **roi/** — ROI files after ImageJ selection (``.roi``).
3'. **roi_cpose/** — ROI files from the Cellpose pipeline *(dev)*.
4. **resize/** → ``*_resize.tif`` — Merged ROI, **scaled RGB** image for registration. Typically use **blue (DAPI)** as reference.
5. **processed/** → ``*_resize_processed.tif`` — Contrast-adjusted and/or rotated image.
6. **transformations/** → ``*_transformed.tif`` — Image after applying the transformation.
7. **transformations/** → ``*_transform_data.mat`` — Transformation matrix/data for each slice.
8. **labelled_regions/** → ``{*channel}_roitable.csv`` — AllenCCF output (per ROI).
9. **labelled_regions/parsed_data/** → ``parsed_csv_merge.csv`` — Parsed & classified CSV for visualization.
10. **resize_overlap/** — If overlap channels exist, mirror the same structure as ``r/g`` channels. **Use the same transformation matrix.** *(optional)*


.. note::

    - For (4): If channel count is limited, save overlap channels to a separate pseudo-color file, then apply **the same** transformation matrix during registration.
    - Ensure the DAPI (blue) channel is used as the registration reference unless otherwise specified.
    - Maintain consistent filename patterns to keep downstream parsing robust.
