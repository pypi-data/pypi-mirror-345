import os
import logging
from silx.io import open as silx_open
from ewokscore import Task
from PIL import Image, TiffImagePlugin

logger = logging.getLogger(__name__)


class TiffFiles(
    Task,
    input_names=[
        "images",
        "output",
    ],
    optional_input_names=["detector_name"],
    output_names=["output_path", "images_list"],
):
    """
    Reads an HDF5 file with frames, extracts each individual frame,
    and saves them as TIFF images in a folder called 'tiff_files'.
    The TIFF images will have a key called imageDescription, default is `eiger`,
    if the detector name is supplied, it will be set accordingly

    The HDF5 file is assumed to contain a 3D dataset (n_frames, height, width)
    at the dataset path "/entry_0000/measurement/data". The output folder is
    created next to the provided output file path.
    """

    def run(self):
        args = self.inputs
        processed_data_dir = os.path.join(os.path.dirname(args.output), "xdi")
        if not os.path.exists(processed_data_dir):
            os.makedirs(processed_data_dir)

        base_name = os.path.splitext(os.path.basename(args.output))[0]

        with silx_open(args.images[0]) as h5file:
            frames = h5file["/entry_0000/measurement/data"][:]

        if frames.ndim != 3:
            raise ValueError(
                "Expected a 3D array (n_frames, height, width), got shape: {}".format(
                    frames.shape
                )
            )

        # Add detector metadata in imageDescription
        tiff_info = TiffImagePlugin.ImageFileDirectory_v2()
        if args.detector_name:
            tiff_info[270] = f"detector={args.detector_name}"
        else:
            tiff_info[270] = "detector=eiger"

        saved_files = []
        for i, frame in enumerate(frames):
            tiff_file_name = "{}_{:04d}.tif".format(base_name, i)
            file_path = os.path.join(processed_data_dir, tiff_file_name)

            im = Image.fromarray(frame)
            im.save(file_path, format="TIFF", tiffinfo=tiff_info)
            saved_files.append(file_path)
        self.outputs.output_path = processed_data_dir
        self.outputs.images_list = saved_files
