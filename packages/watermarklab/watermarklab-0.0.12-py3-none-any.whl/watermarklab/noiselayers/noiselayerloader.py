import torch
import random
from torch import nn
from typing import List
from watermarklab.noiselayers.diffdistortions import *
from watermarklab.utils.basemodel import BaseDiffNoiseModel


class DigitalDistortion(nn.Module):
    """
    A class that applies various digital distortion effects to images.

    This class supports dynamic adjustment of the number of distortions applied
    to a marked image based on the current training step. It provides two modes
    for adjusting the number of applied noise layers: 'parabolic' and 'stair'.

    Attributes:
        max_step (int): Maximum number of steps for training, controlling distortion application.
        k_min (int): Minimum number of distortions to apply.
        k_max (int): Maximum number of distortions to apply.
        noise_layers (dict): A dictionary of noise layer instances.
    """

    def __init__(self, noise_dict: dict, max_step: int = 100, k_min: int = 1, k_max: int = 2):
        """
        Initializes the DigitalDistortion class.

        Args:
            noise_dict (dict): A dictionary specifying the noise layers to include.
                               Keys are layer names, and values are their parameters.
            max_step (int): The maximum number of training steps. Default is 100.
            k_min (int): The minimum number of noise layers to apply. Default is 1.
            k_max (int): The maximum number of noise layers to apply. Default is 2.
        """
        super(DigitalDistortion, self).__init__()
        self.max_step = max_step
        self.k_max = min(k_max, len(noise_dict))
        self.k_min = k_min

        self.noise_dict = noise_dict
        # Predefined noise layers
        self.noise_layers = dict()
        for key in noise_dict.keys():
            if key == "Jpeg":
                self.noise_layers["Jpeg"] = JpegMask(max_step=max_step, Q=noise_dict[key])
            if key == "Resize":
                self.noise_layers["Resize"] = Resize(max_step=max_step, scale_p=noise_dict[key])
            if key == "GaussianBlur":
                self.noise_layers["GaussianBlur"] = GaussianBlur(max_step=max_step, sigma=noise_dict[key])
            if key == "GaussianNoise":
                self.noise_layers["GaussianNoise"] = GaussianNoise(max_step=max_step, std=noise_dict[key])
            if key == "Brightness":
                self.noise_layers["Brightness"] = Brightness(max_step=max_step, brightness_factor=noise_dict[key])
            if key == "Contrast":
                self.noise_layers["Contrast"] = Contrast(max_step=max_step, contrast_factor=noise_dict[key])
            if key == "Saturation":
                self.noise_layers["Saturation"] = Saturation(max_step=max_step, saturation_factor=noise_dict[key])
            if key == "Hue":
                self.noise_layers["Hue"] = Hue(max_step=max_step, hue_factor=noise_dict[key])
            if key == "Rotate":
                self.noise_layers["Rotate"] = Rotate(max_step=max_step, angle=noise_dict[key])
            if key == "SaltPepperNoise":
                self.noise_layers["SaltPepperNoise"] = SaltPepperNoise(max_step=max_step, noise_ratio=noise_dict[key])
            if key == "MedianFilter":
                self.noise_layers["MedianFilter"] = MedianFilter(max_step=max_step, kernel=noise_dict[key])
            if key == "Cropout":
                self.noise_layers["Cropout"] = Cropout(max_step=max_step, crop_ratio_max=noise_dict[key])
            if key == "Dropout":
                self.noise_layers["Dropout"] = Dropout(max_step=max_step, drop_prob=noise_dict[key])
            if key == "Identity":
                self.noise_layers["Identity"] = Identity(max_step=max_step)
            if key == "RandomCompensateTrans":
                self.noise_layers["RandomCompensateTrans"] = RandomCompensateTransformer(max_step=max_step, shift_d=noise_dict[key])

    def stair_k(self, now_step: int) -> int:
        """
        Determines the number of noise layers to apply using a stair-step approach.

        Args:
            now_step (int): Current step in the training process.

        Returns:
            int: Number of noise layers to apply.
        """
        total_steps = self.k_max
        max_steps_per_k = self.max_step / total_steps
        step_index = int(now_step // max_steps_per_k)
        k = self.k_min + step_index
        return min(k, self.k_max)

    def parabolic_k(self, now_step: int, gamma: float = 1.3) -> int:
        """
        Determines the number of noise layers to apply using a parabolic approach.

        Args:
            now_step (int): Current step in the training process.
            gamma (float): Parameter that controls the curvature of the parabola.

        Returns:
            int: Number of noise layers to apply, clamped to a minimum of 1.
        """
        factor = 1.0 if now_step > self.max_step else (now_step / self.max_step) ** gamma
        k = self.k_min + (self.k_max - self.k_min) * factor
        return max(1, int(k))

    def forward(self, marked_img: torch.Tensor, cover_img: torch.Tensor, now_step: int = 0) -> torch.Tensor:
        """
        Applies a random selection of noise layers to the input image.

        Args:
            marked_img (torch.Tensor): The image tensor to which distortions are applied.
            cover_img (torch.Tensor): The cover image tensor used for certain distortions.
            now_step (int): Current step in the training process.

        Returns:
            torch.Tensor: The distorted image tensor with values clamped to the range [0, 1].
        """
        # Determine the number of noise layers to apply
        k = self.stair_k(now_step)

        # Select random noise layers
        selected_keys = random.sample(list(self.noise_layers.keys()), k)

        # Apply selected noise layers sequentially
        noised_img = marked_img
        for key in selected_keys:
            noised_img = self.noise_layers[key](noised_img, cover_img, now_step)
        return noised_img.clamp(0, 1)  # Clamp pixel values to ensure valid range


class DistortionLoader(nn.Module):
    """
    A module that applies a sequence of noise layers to an image, simulating distortions.

    Parameters:
    -----------
    noise_list : List[BaseDiffNoiseModel]
        A list of noise models that will be applied sequentially.
    max_step : int, optional (default=100)
        The maximum training step, used for scheduling the number of applied noise layers.
    k_min : int, optional (default=1)
        The minimum number of noise layers to apply.
    k_max : int, optional (default=2)
        The maximum number of noise layers to apply. If larger than `len(noise_list)`, it will be clipped.

    Methods:
    --------
    stair_k(now_step: int) -> int:
        Determines the number of noise layers (`k`) to apply based on a step-wise (staircase) schedule.
    parabolic_k(now_step: int, gamma: float = 1.3) -> int:
        Determines `k` using a parabolic function, allowing a smooth increase over time.
    forward(marked_img: torch.Tensor, cover_img: torch.Tensor, now_step: int = 0) -> torch.Tensor:
        Applies `k` randomly selected noise layers sequentially to the marked image.
    """

    def __init__(self, noise_list: List[BaseDiffNoiseModel], k_mode: str = "stair_k", k_min: int = 1, k_max: int = 2,
                 max_step=1):
        super(DistortionLoader, self).__init__()
        assert k_mode in ["stair_k", "parabolic_k"]
        self.k_mode = k_mode
        self.max_step = max_step
        self.k_min = k_min  # The minimum number of noise layers to apply
        self.k_max = min(k_max, len(noise_list))  # Ensure k_max does not exceed the available noise layers

        self.noise_list = noise_list
        self.noise_list.sort(key=lambda x: x.noise_name)
        # Ensure the noise list is sorted if required (note: sorting may require defining a comparison key)
        # self.noise_list.sort(key=lambda x: x.some_attribute)  # Uncomment and modify if sorting is necessary

    def stair_k(self, now_step: int) -> int:
        """
        Determines the number of noise layers (`k`) to apply using a staircase function.
        The number of noise layers increases in discrete steps as training progresses.

        Parameters:
        -----------
        now_step : int
            The current training step.

        Returns:
        --------
        k : int
            The number of noise layers to apply.
        """
        if self.k_max == self.k_min:
            return self.k_min  # Avoid division by zero if k_max == k_min

        total_steps = self.k_max - self.k_min + 1  # Total steps for transitioning between k_min and k_max
        max_steps_per_k = self.max_step / total_steps  # Steps required before incrementing k
        step_index = int(now_step // max_steps_per_k)  # Determine which level k should be at
        k = self.k_min + step_index
        return min(k, self.k_max)  # Ensure k does not exceed k_max

    def parabolic_k(self, now_step: int, gamma: float = 1.3) -> int:
        """
        Determines the number of noise layers (`k`) using a parabolic growth function.
        The number of layers smoothly increases over time.

        Parameters:
        -----------
        now_step : int
            The current training step.
        gamma : float, optional (default=1.3)
            A parameter controlling the curvature of the growth function.

        Returns:
        --------
        k : int
            The number of noise layers to apply.
        """
        # Factor smoothly transitions from 0 to 1 as training progresses
        factor = 1.0 if now_step >= self.max_step else (now_step / self.max_step) ** gamma
        k = self.k_min + (self.k_max - self.k_min) * factor  # Compute k using the parabolic function
        return max(self.k_min, int(k))  # Ensure k is at least k_min

    def forward(self, marked_img: torch.Tensor, cover_img: torch.Tensor, now_step: int = 0) -> torch.Tensor:
        """
        Applies randomly selected noise layers to the marked image.

        Parameters:
        -----------
        marked_img : torch.Tensor
            The input image to which noise is applied.
        cover_img : torch.Tensor
            The original reference image (may be used by noise models).
        now_step : int, optional (default=0)
            The current training step, used to determine `k`.

        Returns:
        --------
        noised_img : torch.Tensor
            The distorted image after applying `k` noise layers.
        """
        # Determine the number of noise layers to apply
        if self.k_mode == "stair_k":
            k = self.stair_k(now_step)  # Alternative: use self.parabolic_k(now_step)
        else:
            k = self.parabolic_k(now_step)  # Alternative: use self.parabolic_k(now_step)

        # Randomly select `k` noise models from the available list
        selected_keys = random.sample(range(len(self.noise_list)), k)

        # Apply the selected noise layers sequentially
        noised_img = marked_img
        for key in selected_keys:
            noised_img = self.noise_list[key](noised_img, cover_img, now_step)

        return noised_img.clamp(0, 1)  # Ensure pixel values remain in the valid range [0, 1]


# Execute the test
if __name__ == "__main__":
    pass
