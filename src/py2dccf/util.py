from pathlib import Path
from typing import NamedTuple, Literal, get_args, Union

import cv2
import numpy as np
from scipy.ndimage import maximum_filter

CHANNEL_TYPE = Literal['red', 'green', 'blue']


class TifFile(NamedTuple):
    image: np.ndarray
    red_channel: np.ndarray
    green_channel: np.ndarray
    blue_channel: np.ndarray

    @property
    def height(self) -> int:
        return self.image.shape[0]

    @property
    def width(self) -> int:
        return self.image.shape[1]

    def generate_filtered_image(self, channel: CHANNEL_TYPE, kernal_size: int = 11):
        """
        TODO try diplib https://stackoverflow.com/questions/56134035/how-to-make-ndimage-filters-maximum-filter-work-like-matlabs-imregionalmax-func
        TODO use origin roi reader from fiji

        :param channel:
        :param kernal_size:
        :return:
        """


        if channel == 'red':
            image = self.red_channel
        elif channel == 'green':
            image = self.green_channel
        elif channel == 'blue':
            image = self.blue_channel
        else:
            raise ValueError(f'{channel} unknown')

        if np.sum(image) == 0:
            return np.zeros_like(image, dtype=np.uint8)
        else:
            return np.array(image == maximum_filter(image, kernal_size))


def load_image_file(file: Union[Path]) -> TifFile:
    img = cv2.imread(str(file))
    b, g, r = cv2.split(img)

    return TifFile(img, r, g, b)


if __name__ == '__main__':
    file = Path('/Users/simon/code/Analysis/test_mat/YW043_2_2_b_selection_processed_transformed.tif')
    tif = load_image_file(file)

    filtered = tif.generate_filtered_image('green', kernal_size=5)

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2)
    ax[0].imshow(tif.green_channel)
    ax[1].imshow(filtered)

    ax[1].sharex(ax[0])
    ax[1].sharey(ax[0])
    #
    plt.show()
