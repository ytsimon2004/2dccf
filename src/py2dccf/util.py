from pathlib import Path
from typing import NamedTuple, Literal, Union

import cv2
import numpy as np

ROI_CHANNEL_TYPE = Literal['red', 'green']


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
