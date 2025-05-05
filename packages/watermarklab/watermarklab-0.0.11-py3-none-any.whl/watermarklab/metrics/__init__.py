import numpy as np
from scipy.ndimage import uniform_filter
from watermarklab.utils.basemodel import BaseMetric

__all__ = ['SSIM', 'PSNR', 'NEB', "BER", "EA", "NC"]


class SSIM(BaseMetric):
    def __init__(self, window_size=11, data_range=255, metric_name: str = "ssim"):
        super().__init__(metric_name)
        self.window_size = window_size
        self.data_range = data_range

    def test(self, img1, img2):
        """
        Compute the Structural Similarity Index (SSIM) between two images.

        :param img1: First image (numpy array).
        :param img2: Second image (numpy array).
        :return: SSIM value.
        """
        # Ensure the images have the same shape
        if img1.shape != img2.shape:
            raise ValueError("Input images must have the same shape.")

        # Constants
        k1 = 0.01
        k2 = 0.03
        C1 = (k1 * self.data_range) ** 2
        C2 = (k2 * self.data_range) ** 2

        # Convert images to float
        img1 = img1.astype(np.float64)
        img2 = img2.astype(np.float64)

        # Compute means using a sliding window
        mu1 = uniform_filter(img1, size=self.window_size, mode='constant')
        mu2 = uniform_filter(img2, size=self.window_size, mode='constant')

        # Compute variances and covariance
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2

        sigma1_sq = uniform_filter(img1 ** 2, size=self.window_size, mode='constant') - mu1_sq
        sigma2_sq = uniform_filter(img2 ** 2, size=self.window_size, mode='constant') - mu2_sq
        sigma12 = uniform_filter(img1 * img2, size=self.window_size, mode='constant') - mu1_mu2

        # Compute SSIM
        numerator = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
        denominator = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
        ssim_map = numerator / denominator

        # Return the mean SSIM value
        return np.mean(ssim_map)


class PSNR(BaseMetric):
    def __init__(self, data_range=255, metric_name: str = "psnr"):
        super().__init__(metric_name)
        self.data_range = data_range

    def test(self, img1, img2):
        """
        Calculate the Peak Signal-to-Noise Ratio (PSNR)

        :param img1: Input image
        :param img2: Target image
        :return: PSNR value in decibels (dB)
        """
        if img1.shape != img2.shape:
            raise ValueError("Input image and target image must have the same dimensions")

        # Compute Mean Squared Error (MSE)
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            return float('inf')  # Identical images

        # Compute PSNR
        psnr_value = 20 * np.log10(self.data_range / np.sqrt(mse))
        return psnr_value


class NEB(BaseMetric):
    def __init__(self, metric_name: str = "neb"):
        super().__init__(metric_name)

    def test(self, ext_bits, target_bits):
        """
        Calculate the Number of Error Bits (NEB)

        :param ext_bits: List of extracted bits
        :param target_bits: List of target bits
        :return: Number of error bits
        """
        if len(ext_bits) != len(target_bits):
            raise ValueError("The lengths of the bit lists must be the same")

        # Calculate the number of error bits
        error_bits = np.sum(np.array(ext_bits) != np.array(target_bits))
        return error_bits


class BER(BaseMetric):
    def __init__(self, metric_name: str = "ber"):
        super().__init__(metric_name)

    def test(self, ext_bits, target_bits):
        """
        Calculate the Bit Error Rate (BER) between the extracted watermark and the target watermark.

        :param ext_bits: List of extracted watermark bits
        :param target_bits: List of target watermark bits
        :return: Bit Error Rate (BER)
        """
        if len(ext_bits) != len(target_bits):
            raise ValueError("The lengths of the extracted bits and target bits must be the same.")

        # Calculate the number of differing bits between the two lists
        error_bits = sum(1 for ext, target in zip(ext_bits, target_bits) if ext != target)

        # Calculate BER
        ber = error_bits / len(target_bits) if len(target_bits) > 0 else 0
        return ber


class NC(BaseMetric):
    def __init__(self, metric_name: str = "normalized_correlation"):
        super().__init__(metric_name)

    def test(self, ext_bits, target_bits):
        """
        Normalized Correlation (NC, Normalized Correlation)

        :param ext_bits: List of extracted bits
        :param target_bits: List of target bits
        :return: NC
        """
        if len(ext_bits) != len(target_bits):
            raise ValueError("The lengths of the bit lists must be the same")

        ext_bits = np.array(ext_bits, dtype=np.float32)
        target_bits = np.array(target_bits, dtype=np.float32)

        numerator = np.sum(ext_bits * target_bits)
        denominator = np.sqrt(np.sum(target_bits ** 2) * np.sum(ext_bits ** 2))

        if denominator == 0:
            return 0.0

        nc_value = numerator / denominator
        return nc_value


class EA(BaseMetric):
    def __init__(self, metric_name: str = "extract_accuracy"):
        super().__init__(metric_name)

    def test(self, ext_bits, target_bits):
        """
        Calculate extraction accuracy

        :param ext_bits: List of extracted bits
        :param target_bits: List of target bits
        :return: Extraction accuracy as the ratio of correct bits
        """
        if len(ext_bits) != len(target_bits):
            raise ValueError("The lengths of the bit lists must be the same")

        # Calculate the accuracy as the ratio of correct bits
        correct_bits = np.sum(np.array(ext_bits) == np.array(target_bits))
        accuracy = correct_bits / len(ext_bits) * 100.
        return accuracy
