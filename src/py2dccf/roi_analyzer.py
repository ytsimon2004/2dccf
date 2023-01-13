import re
from pathlib import Path
from typing import List, Union, Tuple, Literal

import numpy as np
import pandas as pd
from PIL import Image
from scipy.io import loadmat

from src.py2dccf.util import load_image_file, load_structure_tree, PLANE_TYPE, allenccf_bregma

ROI_CHANNEL = Literal['r', 'g', 'rg']


class ROIAnalyzer:

    # TODO port to project directory in rscvp
    def __init__(self,
                 path: Path,
                 ref_path: Path,
                 roi_channel: ROI_CHANNEL,
                 plane: PLANE_TYPE):
        """

        :param path: transformation folder
        :param ref_path
        :param roi_channel
        :param plane
        """

        self.path = path
        self.ref_path = ref_path
        self.roi_channel = roi_channel
        self.plane = plane

        self.roi_annotation: dict = dict(avIndex=[], name=[], acronym=[])

        self._bregma = allenccf_bregma()
        self._atlas_res = 0.01  # mm

    @property
    def data(self) -> List[Path]:  # TODO sorted?
        return list(self.path.glob('*transform_data.mat'))

    @property
    def images(self) -> List[Path]:
        return list(self.path.glob('*transformed.tif'))

    @property
    def annotation_file(self) -> np.ndarray:
        return np.load(self.ref_path / 'annotation_volume_10um_by_index.npy')

    @property
    def av_plot(self) -> np.ndarray:
        """plane orientation"""
        av = self.annotation_file
        if self.plane == 'coronal':
            return av  # (1320, 800, 1140)
        elif self.plane == 'sagittal':
            x, y, z = av.shape
            return av.reshape((z, y, x))
        elif self.plane == 'transverse':
            x, y, z = av.shape
            return av.reshape((y, z, x))
        else:
            raise ValueError(f'{self.plane} unknown')

    @property
    def structure_tree(self) -> pd.DataFrame:
        return load_structure_tree(self.ref_path / 'structure_tree_safe_2017.csv')

    @property
    def save_folder(self) -> Path:
        return self.path / 'labelled_region'

    def _foreach_channel_rois(self,
                              rois: np.ndarray,
                              slice_angle: np.ndarray,
                              slice_num: int) -> pd.DataFrame:
        """

        :param rois: binarized image array of roi selection
        :return:
        """
        _, *ref_size = self.av_plot.shape
        if rois.shape != tuple(ref_size):
            raise RuntimeError('roi image is not the right size')

        pixel_row, pixel_col = np.where(rois > 0)

        rois_loc = np.zeros((len(pixel_row), 3))

        offset_map = self._get_offset_map(slice_angle, ref_size)
        bregma = self._bregma
        res = self._atlas_res

        for i, (pr, pc) in enumerate(zip(pixel_row, pixel_col)):
            offset = offset_map[pc, pr]

            if self.plane == 'coronal':
                ap = -(slice_num - bregma[0] + offset) * res
                dv = (pr - bregma[1]) * res
                ml = (pc - bregma[2]) * res
            elif self.plane == 'sagittal':
                ap = -(pc - bregma[0]) * res
                dv = (pr - bregma[1]) * res
                ml = -(slice_num - bregma[2] + offset) * res
            elif self.plane == 'transverse':
                ap = -(pc - bregma[0]) * res
                dv = -(slice_num - bregma[1] + offset) * res
                ml = (pr - bregma[2]) * res
            else:
                raise ValueError(f'unknown {self.plane}')

            rois_loc[i, :] = (ap, dv, ml)

            # finally, find the annotation, name, and acronym of the current ROI pixel
            annot = self.av_plot[int(slice_num + offset), pr, pc]
            self.roi_annotation['avIndex'].append(annot)
            self.roi_annotation['name'].append(self.structure_tree['safe_name'][annot])
            self.roi_annotation['acronym'].append(self.structure_tree['acronym'][annot])

        self.roi_annotation['AP_location'] = rois_loc[:, 0]
        self.roi_annotation['DV_location'] = rois_loc[:, 1]
        self.roi_annotation['ML_location'] = rois_loc[:, 2]

        return pd.DataFrame.from_dict(self.roi_annotation)

    @staticmethod
    def _get_offset_map(slice_angle: np.ndarray, ref_size: Tuple[int, int]) -> np.ndarray:
        """
        Generate offset map (for third dimension of a tilted slice)
        from allenCCF/Browsing Functions/get_offset_map.m

        ..seealso::

            :func:`matlab.img.get_offset_map.m`

        :param slice_angle: (2,)
        :param ref_size: (height, width)
        :return:
            TODO
        """
        angle_ap = int(slice_angle[0])
        angle_ml = int(slice_angle[1])

        ap_frame = np.round(np.linspace(-angle_ap, angle_ap, ref_size[0])).astype(int)
        ml_frame = np.round(np.linspace(-angle_ml, angle_ml, ref_size[1])).astype(int)

        return ap_frame[None, :] + ml_frame[:, None]

    def run_analysis(self):
        # table = np.zeros((len(self.images), len(self.roi_channel)))  # TODO check
        for i, img in enumerate(self.images):
            img_name = self.images[i].name
            tmp = [pattern.start() for pattern in re.finditer('_', img_name)]
            print(f'{i + 1} of {len(self.images)}')
            data = self.data[i]

            # load transformed slice image and transformed matrix
            slice_img = load_image_file(img)  # transformed
            mat = loadmat(data, squeeze_me=True, struct_as_record=False)['save_transform']

            # get the position within the atlas data of the transformed slice
            slice_num: int = mat.allen_location[0]
            slice_angle: np.ndarray = mat.allen_location[1]

            blue = slice_img.blue_channel

            if self.roi_channel == 'r':
                rois = slice_img.local_maxima_image('red')

            elif self.roi_channel == 'g':
                rois = slice_img.local_maxima_image('green')
            else:
                raise NotImplementedError('')

            df = self._foreach_channel_rois(rois, slice_angle, slice_num)
            print(df.to_markdown())


if __name__ == '__main__':
    path = Path('/Users/simon/code/Analysis/test_mat')
    ref = Path('/Users/simon/code/Analysis/histology/reference-atlas-files')

    ra = ROIAnalyzer(path, ref, 'r', 'coronal')
    ra.run_analysis()
