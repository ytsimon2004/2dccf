import re
from pathlib import Path
from typing import List, Union

import numpy as np
from PIL import Image
from scipy.io import loadmat

from src.py2dccf.util import load_image_file


class ROIAnalyzer:

    # TODO port to project directory in rscvp
    def __init__(self,
                 path: Path,
                 ref_path: Path,
                 n_ch: int):
        """

        :param path: transformation folder
        """

        self.path = path
        self.ref_path = ref_path
        self.n_ch = n_ch

    @property
    def data(self) -> List[Path]:  # TODO sorted?
        return list(self.path.glob('*transform_data.mat'))

    @property
    def images(self) -> List[Path]:
        return list(self.path.glob('*transformation.tif'))

    @property
    def annotation_file(self) -> Path:
        return self.ref_path / 'annotation_volume_10um_by_index.npy'

    @property
    def structure_tree(self) -> Path:
        return self.ref_path / 'structure_tree_safe_2017.csv'

    @property
    def save_folder(self) -> Path:
        return self.path / 'labelled_region'

    def analysis(self):
        table = np.zeros(len(self.images), self.n_ch)
        for i, img in enumerate(self.images):
            img_name = self.images[i].name
            tmp = [pattern.start() for pattern in re.finditer('_', img_name)]
            print(f'{i} of {len(self.images)}')
            data = self.data[i]

            # load transformed slice image and transformed matrix
            slice_img = load_image_file(img)  # transformed
            mat = loadmat(data, squeeze_me=True, struct_as_record=False)['save_transform']

            # get the position within the atlas data of the transformed slice
            slice_num = mat.allen_location[0]
            slice_angle = mat.allen_location[1]

            roi_r = slice_img.red_channel
            roi_g = slice_img.green_channel
            blue = slice_img.blue_channel
