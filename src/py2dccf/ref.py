import warnings
from pathlib import Path
from typing import Dict, NamedTuple, Tuple

import cv2
import numpy as np
import pandas as pd
import scipy.io as sio
from rich import print
from scipy.ndimage import maximum_filter

from src.slack_bot.bot import slack_bot
from src.util.argp import AbstractParser, argument
from src.util.cli_hist import HistOptions, PLANE_TYPE, RegDirInfo
from .util import allenccf_bregma


# todo read transform matrix
# todo read roi position from ROIPARA
# todo replace tif roi_total with transform roi position
# todo no need tif image anymore (including)

class RoiMapOption(AbstractParser, HistOptions):
    DESCRIPTION = 'generate the output labelled_regions based on transformed tif and mat'

    channel: str = argument(
        '-C', '--channel',
        default='rg',
        help='combination of "r", "g" and "b"',
    )

    output_fname: Path = argument(
        '-o', '--output',
        metavar='PATH',
        default=Path('output.csv'),
        help='output .csv filename',
    )

    @slack_bot()
    def run(self):
        regdir = self.get_reg_dir(self.glass_id, self.slice_id)
        self.generate_roi_map(regdir, self.channel, self.plane, output_name=self.output_fname)

    @staticmethod
    def generate_roi_map(info: RegDirInfo,
                         n_rgb: str = 'rg',
                         plane: PLANE_TYPE = 'coronal',
                         av: np.ndarray = None,
                         st: pd.DataFrame = None,
                         output_name: str = 'output.csv') -> pd.DataFrame:
        """
        annotate roi to specific brain areas after registration using allenCCF

        ..seealso::

            :func:`matlab.img.Analyze_ROIs_Update.m`


        :param info: 'RegDirInfo'
        :param n_rgb: combination of three characters 'r', 'g' and 'b'
        :param plane
        :param av: 'annotation_volume_10um_by_index.npy'
        :param st: 'structure_tree_safe_2017.csv'
        :param output_name: output_file in the labelled_region file

        :return:
        """
        if len(n_rgb) == 0:
            raise ValueError('empty channel')
        elif len(set(n_rgb).difference('rgb')) != 0:
            raise ValueError(f'unknown channel : {n_rgb}')
        elif len(n_rgb) != len(set(n_rgb)):
            raise ValueError(f'duplicate channel : {n_rgb}')

        # after transformation
        # if len(info) == 0:
        #     raise FileNotFoundError(f'no tif found under {info.data_root}')

        if not info.labelled_roi_folder.exists():
            info.labelled_roi_folder.mkdir(parents=True)
            print(f'[bold yellow]create {info.labelled_roi_folder} output directory')

        # load the reference brain annotations
        if av is None or st is None:
            print('[bold yellow]loading reference atlas...')
            av = info.annotation_data()
            st = info.structure_data()

        # select the plane for the viewer
        if plane == 'coronal':
            av_plot = av  # (1320, 800, 1140)
        elif plane == 'sagittal':
            x, y, z = av.shape
            av_plot = av.reshape((z, y, x))
        elif plane == 'transverse':
            x, y, z = av.shape
            av_plot = av.reshape((y, z, x))
        else:
            raise ValueError(f'{plane} unknown')

        table_ls = []
        for tif_path in info:
            tif_file = info.get_processed_tif(tif_path)
            mat_file = info.get_transform_mat(tif_path)
            t_matrix = info.get_transform_matrix(tif_path)  # todo further work

            if not tif_file.exists():
                warnings.warn(f'tif file not found {tif_file}')
                continue
            if not mat_file.exists():
                warnings.warn(f'mat file not found {mat_file}')
                continue

            mdata = _read_mat(mat_file)
            tdata = _load_image(tif_file)

            for channel in n_rgb:
                ret = _foreach_channel(tdata.get_channel(channel), av_plot, mdata, plane, st)
                ret['source'] = tif_path.stem
                ret['channel'] = channel
                table_ls.append(ret)

        coordinates = pd.concat(table_ls, ignore_index=True)
        # todo append if multiple files
        output_file = (info.labelled_roi_folder / output_name).with_suffix('.csv')
        coordinates.to_csv(output_file)
        print(f'[bold yellow]Finished, Check {output_file}...')

        return coordinates


class TifData(NamedTuple):
    tif_file: Path
    rois: np.ndarray
    roi_r: np.ndarray  # (yP, xP)
    roi_g: np.ndarray  # (yP, xP)
    roi_b: np.ndarray  # (yP, xP)

    @property
    def shape(self) -> Tuple[int, int, int]:
        return self.rois.shape

    def get_channel(self, ch: str) -> np.ndarray:
        # if the rois come from a transformed roi image of non-contiguous roi
        # pixels (e.g. an ROI pixel for each neuron), then run this line to ensure
        # a one-to-one mapping between ROIs in the original and transformed images

        filter_kernel = 11
        if ch == 'r':
            if np.sum(self.roi_r) == 0:
                return np.zeros_like(self.roi_r, dtype=np.uint8)
            else:
                return np.array(self.roi_r == maximum_filter(self.roi_r, filter_kernel), dtype=np.uint8)
        elif ch == 'g':
            if np.sum(self.roi_g) == 0:
                return np.zeros_like(self.roi_g, dtype=np.uint8)
            else:
                return np.array(self.roi_g == maximum_filter(self.roi_g, filter_kernel), dtype=np.uint8)
        elif ch == 'b':
            if np.sum(self.roi_b) == 0:
                return np.zeros_like(self.roi_b, dtype=np.uint8)
            else:
                return np.array(self.roi_b == maximum_filter(self.roi_b, filter_kernel), dtype=np.uint8)
        else:
            raise ValueError()


def _load_image(tif_file: Path) -> TifData:
    """

    :param tif_file:
    :return:
    """
    # load and extract roi channel
    rois = cv2.imread(str(tif_file))  # (800, 1140, 3) if coronal
    roi_b, roi_g, roi_r = cv2.split(rois)

    return TifData(tif_file, rois, roi_r, roi_g, roi_b)


class MatData(NamedTuple):
    mat_file: Path
    n_slice: int
    slice_angle: np.ndarray  # shape (2,) number of different slices between center and the end point


def _read_mat(mat_file: Path) -> MatData:
    """read .mat in the processed folder"""
    trans_info = sio.loadmat(mat_file, squeeze_me=True)  # type: Dict
    trans_info = trans_info['save_transform']

    # get the actual transformation from slice to atlas
    n_slice = trans_info['allen_location'].item()[0]
    print('[bold cyan]n_slice', n_slice)
    slice_angle = trans_info['allen_location'].item()[1]
    print('[bold cyan]slice_angle', slice_angle)

    return MatData(mat_file, n_slice, slice_angle)


def _foreach_channel(rois_cur: np.ndarray,
                     av_plot: np.ndarray,
                     mdata: MatData,
                     plane: PLANE_TYPE,
                     st: pd.DataFrame) -> pd.DataFrame:
    """

    :param av_plot:
    :return: data frame with header
        avIndex: int
        name: str
        acronym: str
        AP_location: float
        DV_location: float
        ML_location: float
    """
    _, *ref_size = av_plot.shape
    if rois_cur.shape != tuple(ref_size):
        raise RuntimeError('roi image is not the right size')

    # get location and annotation for every roi pixel
    pixel_row, pixel_column = np.where(rois_cur > 0)
    print('[bold cyan]roicur', rois_cur.shape)

    img_name = np.zeros((len(pixel_row), 3))  # todo might need to rename to roi_loc, so da caller?
    roi_annot = dict(
        avIndex=[],
        name=[],
        acronym=[]
    )

    # generate other necessary values
    bregma = allenccf_bregma()  # bregma position in reference data space
    atlas_resolution = 0.01  # mm
    offset_map = _get_offset_map(mdata.slice_angle, ref_size)

    for i, (pr, pc) in enumerate(zip(pixel_row, pixel_column)):
        # get the offset from the AP value at the centre of the slice, due to off-from-coronal angling
        offset = offset_map[pc, pr]  # todo check

        # use this and the slice number to get the AP, DV, and ML coordinates
        if plane == 'coronal':
            ap = -(mdata.n_slice - bregma[0] + offset) * atlas_resolution
            dv = (pr - bregma[1]) * atlas_resolution
            ml = (pc - bregma[2]) * atlas_resolution
        elif plane == 'sagittal':
            ap = -(pc - bregma[0]) * atlas_resolution
            dv = (pr - bregma[1]) * atlas_resolution
            ml = -(mdata.n_slice - bregma[2] + offset) * atlas_resolution
        elif plane == 'transverse':
            ap = -(pc - bregma[0]) * atlas_resolution
            dv = -(mdata.n_slice - bregma[1] + offset) * atlas_resolution
            ml = (pr - bregma[2]) * atlas_resolution
        else:
            raise ValueError(f'unknown {plane}')

        img_name[i, :] = (ap, dv, ml)

        # finally, find the annotation, name, and acronym of the current ROI pixel
        annot = av_plot[int(mdata.n_slice + offset), pr, pc]
        roi_annot['avIndex'].append(annot)
        roi_annot['name'].append(st['safe_name'][annot])
        roi_annot['acronym'].append(st['acronym'][annot])

    roi_annot['AP_location'] = img_name[:, 0]
    roi_annot['DV_location'] = img_name[:, 1]
    roi_annot['ML_location'] = img_name[:, 2]
    return pd.DataFrame.from_dict(roi_annot)


def _get_offset_map(slice_angle: np.ndarray, ref_size: Tuple[int, int]) -> np.ndarray:
    """
    Generate offset map (for third dimension of a tilted slice)
    from allenCCF/Browsing Functions/get_offset_map.m

    ..seealso::

        :func:`matlab.img.get_offset_map.m`

    :param slice_angle: (2,)
    :param ref_size: (height, width)
    :return:
    """
    angle_ap = int(slice_angle[0])
    angle_ml = int(slice_angle[1])

    ap_frame = np.round(np.linspace(-angle_ap, angle_ap, ref_size[0])).astype(int)
    ml_frame = np.round(np.linspace(-angle_ml, angle_ml, ref_size[1])).astype(int)

    return ap_frame[None, :] + ml_frame[:, None]


if __name__ == '__main__':
    RoiMapOption().main()
