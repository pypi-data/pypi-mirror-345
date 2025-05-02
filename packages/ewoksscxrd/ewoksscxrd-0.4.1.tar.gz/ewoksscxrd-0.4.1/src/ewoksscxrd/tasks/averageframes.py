import os
import logging
import numpy as np
from silx.io import open as silx_open
from ewokscore import Task
from fabio.edfimage import EdfImage

logger = logging.getLogger(__name__)


class averageFrames(
    Task,
    input_names=["images", "output"],
    output_names=["output_path", "image"],
):
    """
    Reads an HDF5 file with frames, averages them along the frame axis,
    and saves the averaged image in EDF format using fabio.
    images is a list of lima HDF5 files.

    The HDF5 file is assumed to contain a 3D dataset (n_frames, height, width).
    By default, it will attempt to use the dataset named "/entry_0000/measurement/data".
    """

    def run(self):
        args = self.inputs
        processed_data_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(args.output))), "edf_PX"
        )
        if not os.path.exists(processed_data_dir):
            os.makedirs(processed_data_dir)
        destination_basename = os.path.basename(args.output) + ".edf"
        with silx_open(args.images[0]) as h5file:
            frames = h5file["/entry_0000/measurement/data"][()]

        # Validate that the data is 3D
        if frames.ndim != 3:
            raise ValueError(
                "Expected a 3D array (n_frames, height, width), got shape: {}".format(
                    frames.shape
                )
            )

        # Compute the average of the frames along the frame dimension (axis=0)
        avg_frame = np.mean(frames, axis=0)

        # Create an EDF image using fabio and save it
        edf_img = EdfImage(data=avg_frame)
        edf_img.write(os.path.join(processed_data_dir, destination_basename))
        self.outputs.output_path = args.output
        self.outputs.image = avg_frame
