from pathlib import Path
from typing import Literal

import cv2
import numpy as np
import pandas as pd

ROI_CHANNEL_TYPE = Literal['red', 'green']
CHANNEL_TYPE = Literal['red', 'green', 'blue', 'overlap']
PLANE_TYPE = Literal['coronal', 'sagittal', 'transverse']


def load_structure_tree(fpath: Path) -> pd.DataFrame:
    """
    todo allenCCF/Browsing Functions/loadStructureTree.m further?

    ..seealso::

        :func:`matlab.img.loadStructureTree.m`

    :param fpath: csv
    :return:
    """
    if '2017' in fpath.name:
        return _load_structure_tree_2017(fpath)
    else:
        return _load_structure_tree_old(fpath)


def _load_structure_tree_2017(fpath: Path) -> pd.DataFrame:
    """
    parse the 'structure_tree_safe_2017.csv' from allenCCF

    :param fpath: 'structure_tree_safe_2017.csv' path
    :return: data frame with header
        id: int
        atlas_id: int, -2 for empty
        name: str
        acronym: str
        st_level: str
        ontology_id: int
        hemisphere_id: int
        weight: int
        parent_structure_id: int, -1 for root
        depth: int
        graph_id: int
        graph_order: int
        structure_id_path: tuple[int]
        color_hex_triplet: str
        neuro_name_structure_id: str
        neuro_name_structure_id_path: str
        failed: str
        sphinx_id: int
        structure_name_facet: int
        failed_facet: int
        safe_name: str
    """
    return pd.read_csv(
        fpath, sep=',',
        converters=dict(
            atlas_id=lambda it: int(float(it)) if len(it) else -2,
            parent_structure_id=lambda it: int(float(it)) if len(it) else -1,
            structure_id_path=lambda it: tuple(map(int, it[1:-1].split('/'))),
            st_level=str,
            neuro_name_structure_id=str,
            neuro_name_structure_id_path=str,
        )
    )


def _load_structure_tree_old(fpath: Path) -> pd.DataFrame:
    """

    :param fpath:
    :return: data frame with header
        acronym: str
        id: int
        name: str
        structure_id_path: tuple[int]
        parent_structure_id: int, -1 for root
        safe_name: str, as same as name
    """
    ret = pd.read_csv(
        fpath, sep=',',
        converters=dict(
            structure_id_path=lambda it: tuple(map(int, it[1:-1].split('/'))),
            parent_structure_id=lambda it: int(float(it)) if len(it) else -1
        )
    )
    ret['safe_name'] = ret['name']
    return ret


def allenccf_bregma() -> np.ndarray:
    """
    Return coordinates of bregma in allen CCF 10um volume coordinates
    from allenCCF/Browsing Functions/allenCCFbregma.m

    :return: AP, DV, ML(LR) coordinate
    """
    return np.array([540, 0, 570])


class ImageReader:

    def __init__(self, file: Path):
        self.file = file

    def __getitem__(self, channel: CHANNEL_TYPE):
        if channel == 'red':
            return cv2.split(self.image)[0]
        elif channel == 'green':
            return cv2.split(self.image)[1]
        elif channel == 'blue':
            return cv2.split(self.image)[2]
        else:
            raise KeyError(f'{channel}')

    @property
    def image(self) -> np.ndarray:
        """rgba images, (H, W, 4)"""
        rgb = cv2.imread(str(self.file))
        rgba = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGBA)
        return np.array(rgba, dtype=np.uint8)

    @property
    def height(self) -> int:
        return self.image.shape[0]

    @property
    def width(self) -> int:
        return self.image.shape[1]

    def view_2d(self, flip=True) -> np.ndarray:
        """view image as 2d array (H, W)"""
        w, h, _ = self.image.shape
        im = self.image.view(dtype=np.uint32).reshape((w, h))
        if flip:
            return np.flipud(im)
        else:
            return im

    def local_maxima_image(self, channel: ROI_CHANNEL_TYPE) -> np.ndarray:
        """
        find the local maxima of the selection points.
        i.e., used in roi selection of the neuron before counting

        :param channel: color of image
        :return:
            (H, W) 2d array
        """
        from skimage.morphology import local_maxima

        image = self[channel]
        if np.sum(image) == 0:
            return np.zeros_like(image, dtype=np.uint8)
        else:
            return local_maxima(image)