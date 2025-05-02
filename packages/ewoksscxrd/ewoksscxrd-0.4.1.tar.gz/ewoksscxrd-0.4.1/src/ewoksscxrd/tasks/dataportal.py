import os
import logging
import numpy as np
from PIL import Image, ImageOps
from ewokscore import Task
from ewokscore.missing_data import MissingData

from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class dataPortal(
    Task,
    input_names=["image", "output"],
    output_names=["gallery_file_path"],
    optional_input_names=[
        "gallery_output_format",
        "gallery_overwrite",
        "gallery_output_binning",
        "bounds",
    ],
):
    """
    Task that builds a gallery by processing an image:
      - Normalizes/clamps the image to 8-bit grayscale.
      - Applies binning with a defined binning factor.
      - Saves the processed image as a PNG (or as specified by gallery_output_format)
        in a folder called "gallery" within the processed data directory.
      - Infers ICAT parameters from the processed data directory and stores
        processed data metadata using pyicat_plus.

    Inputs:
      - image: A 2D numpy.ndarray (or a 3D array with a singleton first dimension).
      - output: A file path; its directory is used as the processed data directory.

    Optional inputs:
      - gallery_output_format: Output image file format (default "png").
      - gallery_overwrite: Whether to overwrite an existing file (default True).
      - gallery_output_binning: Binning factor (default 1, meaning no binning).
      - bounds: A tuple (lower_bound, upper_bound) used for normalization.
                If not provided, lower_bound defaults to 0 and upper_bound is set to the 99.9th percentile
                of pixel values below 65,000, with any pixel at or above 65,000 set to 0.
                This generated image is only for display purposes.
    """

    def run(self):
        args = self.inputs
        # Check for MissingData and assign defaults.
        self.gallery_output_format = getattr(args, "gallery_output_format", "png")
        if isinstance(self.gallery_output_format, MissingData):
            self.gallery_output_format = "png"
        self.gallery_overwrite = getattr(args, "gallery_overwrite", True)
        if isinstance(self.gallery_overwrite, MissingData):
            self.gallery_overwrite = True
        self.gallery_output_binning = getattr(args, "gallery_output_binning", 2)
        if isinstance(self.gallery_output_binning, MissingData):
            self.gallery_output_binning = 2
        bounds = getattr(args, "bounds", None)
        if isinstance(bounds, MissingData):
            bounds = None

        # Use the directory of the output file as the processed data directory.
        processed_data_dir = os.path.dirname(args.output)
        gallery_dir = self.get_gallery_dir(processed_data_dir)
        os.makedirs(gallery_dir, exist_ok=True)

        # Construct the output file name based on the provided output path.
        gallery_file_name = os.path.basename(args.output)
        if not gallery_file_name.endswith(f".{self.gallery_output_format}"):
            gallery_file_name += f"_average.{self.gallery_output_format}"
        gallery_file_path = os.path.join(gallery_dir, gallery_file_name)

        # Process the image and save it in the gallery.
        self.save_to_gallery(gallery_file_path, args.image, bounds)
        self.outputs.gallery_file_path = gallery_file_path

        # Infer ICAT parameters from processed_data_dir and store processed data metadata.
        try:
            self.store_to_icat()
        except Exception as e:
            logger.warning("Error storing processed data to ICAT: %s", e)

    def get_gallery_dir(self, processed_data_dir: str) -> str:
        """
        Returns the path to the gallery folder inside the processed data directory.
        """
        return os.path.join(processed_data_dir, "gallery")

    def _bin_data(self, data: np.ndarray, binning: int) -> np.ndarray:
        """
        Bins a 2D array by the specified binning factor.
        If binning <= 1, returns the original data.
        """
        if binning <= 1:
            return data
        h, w = data.shape
        new_h = h // binning
        new_w = w // binning
        # Crop the image if necessary so dimensions are divisible by the binning factor.
        data_cropped = data[: new_h * binning, : new_w * binning]
        # Reshape and compute the mean over each bin.
        binned = data_cropped.reshape(new_h, binning, new_w, binning).mean(axis=(1, 3))
        return binned

    def save_to_gallery(
        self,
        output_file_name: str,
        image: np.ndarray,
        bounds: "Optional[Tuple[float, float]]" = None,
    ) -> None:
        """
        Processes and saves the image to the gallery folder:
          - If the image is 3D with a singleton first dimension, reshapes it to 2D.
          - Normalizes the image to 8-bit grayscale using the provided bounds if available.
            If no bounds are provided, lower_bound defaults to 0 and upper_bound is set to the 99.9th percentile
            of pixels below 65,000. Also, any pixel with a value at or above 65,000 is set to 0. This is designed to handle the case of saturated pixels.
          - Applies binning based on gallery_output_binning.
          - Saves the result as an image in the specified output format.
        """
        overwrite = self.gallery_overwrite
        binning = self.gallery_output_binning

        # Ensure the image is 2D. If it's 3D with a single channel, squeeze it.
        if image.ndim == 3 and image.shape[0] == 1:
            image = image.reshape(image.shape[1:])
        elif image.ndim != 2:
            raise ValueError(f"Only 2D grayscale images are handled. Got {image.shape}")

        # Check if bounds is a valid tuple; otherwise use defaults.
        if not isinstance(bounds, tuple):
            lower_bound = 0
            valid_pixels = image[image < 65000]
            if valid_pixels.size > 0:
                upper_bound = np.percentile(valid_pixels, 99.9)
            else:
                upper_bound = 65000
            # Handle saturation: set any pixel at or above 65,000 to 0.
            image = np.where(image >= 65000, 0, image)
        else:
            lower_bound, upper_bound = bounds

        # Apply clamping and normalization.
        image = np.clip(image, lower_bound, upper_bound)
        image = image - lower_bound
        if upper_bound != lower_bound:
            image = image * (255.0 / (upper_bound - lower_bound))

        # Apply binning if necessary.
        image = self._bin_data(data=image, binning=binning)

        # Convert the image to a PIL Image.
        img = Image.fromarray(image.astype(np.uint8), mode="L")
        # Invert the colormap.
        img = ImageOps.invert(img)
        if not overwrite and os.path.exists(output_file_name):
            raise OSError(f"File already exists ({output_file_name})")
        img.save(output_file_name)

    def store_to_icat(self) -> None:
        """
        Infers ICAT parameters from the processed data directory and stores processed data information
        using pyicat_plus.

        The processed_data_dir (icat_processed_path) is taken from the directory of the output path.
        For a processed_data_dir like:

            /data/visitor/proposal/beamline/sessions/PROCESSED_DATA/sample/sample_dataset

        the parameters are inferred as follows:
          - icat_processed_path: Same as processed_data_dir.
          - icat_proposal: "proposal" (4th element).
          - icat_beamline: "beamline" (5th element).
          - icat_dataset: "sample_dataset" (last element).
          - icat_raw: Replace "PROCESSED_DATA" with "RAW_DATA" in the processed_data_dir.
          - icat_metadata: {} (an empty dictionary).
        """
        args = self.inputs
        # Use the directory of the output file as the processed data directory.
        icat_processed_path = os.path.dirname(args.output)
        # Normalize and split the path.
        path_parts = os.path.normpath(icat_processed_path).split(os.sep)
        try:
            # Expected structure: ['', 'data', 'visitor', 'proposal', 'beamline', 'sessions', 'PROCESSED_DATA', 'sample', 'sample_dataset', 'scan0001']
            proposal = path_parts[3]
            beamline = path_parts[4]
            dataset = path_parts[-2]
            sample_name = path_parts[-3]
        except IndexError:
            logger.warning(
                "Could not infer ICAT parameters from processed_data_dir: %s",
                icat_processed_path,
            )
            return
        # Construct icat_raw by replacing PROCESSED_DATA with RAW_DATA in the processed path.
        icat_raw = os.path.dirname(icat_processed_path).replace(
            "PROCESSED_DATA", "RAW_DATA"
        )
        icat_metadata = {"Sample_name": sample_name}

        from pyicat_plus.client.main import IcatClient
        from pyicat_plus.client import defaults

        client = IcatClient(metadata_urls=defaults.METADATA_BROKERS)
        client.store_processed_data(
            beamline=beamline,
            proposal=proposal,
            dataset=dataset,
            path=icat_processed_path,
            raw=[icat_raw],
            metadata=icat_metadata,
        )
        client.disconnect()
