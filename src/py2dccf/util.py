from pathlib import Path
from typing import NamedTuple, Literal, Union
import pandas as pd
import cv2
import numpy as np

ROI_CHANNEL_TYPE = Literal['red', 'green']
PLANE_TYPE = Literal['coronal', 'sagittal', 'transverse']


class TifFile(NamedTuple):
    image: np.ndarray
    red_channel: np.ndarray
    green_channel: np.ndarray
    blue_channel: np.ndarray
    """normally reference channel. i.e., DAPI"""

    @property
    def height(self) -> int:
        return self.image.shape[0]

    @property
    def width(self) -> int:
        return self.image.shape[1]

    def local_maxima_image(self, channel: ROI_CHANNEL_TYPE) -> np.ndarray:
        """

        :param channel:
        :return:
        """
        from skimage.morphology import local_maxima

        if channel == 'red':
            image = self.red_channel
        elif channel == 'green':
            image = self.green_channel
        else:
            raise ValueError(f'{channel} unknown')

        if np.sum(image) == 0:
            return np.zeros_like(image, dtype=np.uint8)
        else:
            return local_maxima(image)


def load_image_file(file: Union[Path]) -> TifFile:
    img = cv2.imread(str(file))
    b, g, r = cv2.split(img)

    return TifFile(img, r, g, b)


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


if __name__ == '__main__':
    file = Path('/Users/simon/code/Analysis/test_mat/YW043_2_2_b_selection_processed_transformed.tif')
    tif = load_image_file(file)

    filtered = tif.local_maxima_image('red')

    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2)
    ax[0].imshow(tif.red_channel)
    ax[1].imshow(filtered)

    ax[1].sharex(ax[0])
    ax[1].sharey(ax[0])
    #
    plt.show()
