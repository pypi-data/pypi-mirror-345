import os
import logging
from ewokscore import Task
from .utils import (
    read_dataset,
    subtract_images_inplace_parallel,
    write_lima_images,
    create_header_from_file,
)
from ewokscore.missing_data import MissingData

logger = logging.getLogger(__name__)


class lima2Thresholding(
    Task,
    input_names=["images", "output", "scale_factor"],
    optional_input_names=["dectris_masking_value"],
    output_names=["output_path"],
):
    """
    Reads a 4D HDF5 file (shape: (nframes, 2, H, W)) and processes each frame as follows:
      - For each pixel, if the value in image1 exceeds dectris_masking_value (optional, default: 1e6),
        the two corresponding pixel values are summed.
      - Otherwise, image1 is scaled by scale_factor and subtracted from image0.
      - Any negative result values after subtraction are set to 0.

    The processed result (a 3D image) is then written to the specified output file in LImA HDF5 format.

    Inputs:
      images: list of input HDF5 files.
      output: destination file path for the processed result.
      scale_factor: scaling factor applied to image1 for subtraction.
      dectris_masking_value: threshold value applied to image1 (optional; default: 2**32 - 1).

    Outputs:
      output_path: final path of the saved file.
    """

    def run(self):
        args = self.inputs
        logger.info("Starting lima2Thresholding task.")

        # Set default dectris_masking_value if not provided
        dectris_masking_value = getattr(args, "dectris_masking_value", None)
        if isinstance(dectris_masking_value, MissingData):
            dectris_masking_value = 2**32 - 1

        processed_data_dir = os.path.dirname(args.output)
        if not os.path.exists(processed_data_dir):
            os.makedirs(processed_data_dir)
            logger.info("Created directory: %s", processed_data_dir)

        destination_basename = os.path.basename(args.output) + "_subtracted.h5"
        output_path = os.path.join(processed_data_dir, destination_basename)
        logger.info("Output file: %s", output_path)

        data = read_dataset(args.images[0])
        logger.info("Dataset shape: %s", data.shape)

        header = create_header_from_file(args.images[0])

        result = subtract_images_inplace_parallel(
            data, args.scale_factor, dectris_masking_value
        )
        logger.info("Result shape: %s", result.shape)

        write_lima_images(result, output_path, header)
        logger.info("Written output to: %s", output_path)

        self.outputs.output_path = [output_path]
        logger.info("lima2Thresholding task completed.")
