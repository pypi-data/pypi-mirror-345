import timeit
import numpy as np
from torch import nn
from numpy import ndarray
from typing import List, Tuple, Any
from abc import ABC, abstractmethod

__all__ = ['Result', 'BaseWatermarkModel', 'BaseDataset', 'NoiseModelWithFactors', 'BaseTestNoiseModel', 'BaseMetric']


class Result:
    """
    The Result class stores the results of watermarking processes, including the embedded image, extracted bits,
    recovered cover image, and other related results.

    Attributes:
        stego_img (ndarray): The image with the embedded watermark.
        ext_bits (list): The extracted watermark bits from the stego image.
        other_result (dict): Other related results, such as performance metrics.
    """

    def __init__(self, stego_img: List[ndarray] = None, ext_bits: List[ndarray] = None, rec_img: List[ndarray] = None,
                 other_result: dict = None):
        # Initialize the result attributes
        self.stego_img = stego_img
        self.ext_bits = ext_bits
        self.other_result = other_result
        self.rec_img = rec_img


def timing_decorator(func):
    def wrapper(self, *args, **kwargs):
        start_time = timeit.default_timer()
        result = func(self, *args, **kwargs)
        end_time = timeit.default_timer()
        result.other_result[func.__name__] = end_time - start_time
        return result
    return wrapper


class BaseWatermarkModel(ABC):
    """
    BaseModel is an abstract class that defines the interface for watermark embedding, extraction, and recovery.
    Subclasses should implement these methods to provide specific watermarking functionality.

    Attributes:
        bits_len (int): The length of the watermark bits.
        img_size (int): The size of the image being processed.
    """

    def __init__(self, bits_len: int, img_size: int, modelname: str):
        # Initialize the basemodel.md, bits length, and image size
        self.modelname = modelname
        self.bits_len = bits_len
        self.img_size = img_size

    @abstractmethod
    @timing_decorator
    def embed(self, cover_list: List[Any], secrets: List[List]) -> Result:
        """
        Embed a watermark into the cover image. This method should be implemented by subclasses to provide
        the specific embedding logic.

        :param self:
        :param cover_list: The cover image, of type ndarray.
        :param secrets: The watermark bits, of type list.
        :return: A Result object containing the embedded image and other related information.
        """
        # Ensure the cover image and watermark are valid
        assert cover_list is not None
        assert secrets is not None and len(secrets) > 0

        # This is a placeholder for actual watermark embedding logic
        return Result()  # Return a Result object containing the embedding result

    @abstractmethod
    @timing_decorator
    def extract(self, stego_list: List[ndarray]) -> Result:
        """
        Extract the watermark from the stego image. This method should be implemented by subclasses to provide
        the specific extraction logic.

        :param self:
        :param stego_list: The stego image with the embedded watermark, of type ndarray.
        :return: A Result object containing the extracted watermark bits and other related information.
        """
        # Ensure the stego image is valid
        assert stego_list is not None

        # This is a placeholder for actual watermark extraction logic
        return Result()  # Return a Result object containing the extraction result

    @abstractmethod
    @timing_decorator
    def recover(self, stego_list: List[ndarray]) -> Result:
        """

        :param stego_list:
        :return:
        """


class BaseDataset(ABC):
    def __init__(self, iter_num: int):
        """
        Base class for loading cover images and generating secret bits.

        Args:
            iter_num (int): Number of experiments to run per cover image.
        """
        self.iter_num = iter_num
        assert iter_num > 0

    @abstractmethod
    def load_cover_secret(self, index: int) -> Tuple[np.ndarray, List]:
        """
        Abstract method to load a cover image and secret by index.

        Args:
            index (int): Index of the cover image to load.

        Returns:
            Tuple[np.ndarray, List]: A tuple containing the cover image (as a numpy array)
                                     and the corresponding secret (as a list).
        """
        pass

    def __getitem__(self, index: int) -> Tuple[np.ndarray, List, int, int]:
        """
        Load a cover image and generate a unique secret for it.

        Args:
            index (int): Index of the experiment (0 to len(self) - 1).

        Returns:
            Tuple[np.ndarray, List]: A tuple containing the cover image and a unique secret.
        """
        # Calculate the cover index
        cover_index = index // self.iter_num

        # Load the cover image and secret
        cover, secret = self.load_cover_secret(cover_index)
        return cover, secret, cover_index, index % self.iter_num

    def __len__(self) -> int:
        """
        Get the total number of experiments (cover images * iter_num).

        Returns:
            int: The total number of experiments.
        """
        return self.get_num_covers() * self.iter_num

    @abstractmethod
    def get_num_covers(self) -> int:
        """
        Abstract method to get the total number of cover images available.

        Returns:
            int: The number of cover images.
        """
        pass


class BaseDiffNoiseModel(nn.Module):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @abstractmethod
    def forward(self, stego_img, cover_img, now_step: int = 0):
        pass


class BaseTestNoiseModel(ABC):
    @abstractmethod
    def test(self, stego_img, cover_img, factor):
        assert stego_img is not None
        assert cover_img is not None

    def print_params(self):
        params_dict = {self.__class__.__name__: vars(self)}
        return params_dict


class BaseMetric(ABC):
    def __init__(self, metric_name: str):
        self.metric_name = metric_name

    @abstractmethod
    def test(self, cover, stego):
        pass


class NoiseModelWithFactors:
    def __init__(self, noisemodel: BaseTestNoiseModel, noisename: str, factors: list, factorsymbol: str):
        """
        Class to encapsulate a noise model with its factors and symbol.

        :param noisemodel: The noise model to apply.
        :param noisename: Name of the noise model.
        :param factors: List of factors to apply with the noise model.
        :param factorsymbol: Symbol representing the factor (e.g., "$Q_f$" for JPEG quality).
        """
        self.factorsymbol = factorsymbol
        self.noisemodel = noisemodel
        self.noisename = noisename
        self.factors = factors
