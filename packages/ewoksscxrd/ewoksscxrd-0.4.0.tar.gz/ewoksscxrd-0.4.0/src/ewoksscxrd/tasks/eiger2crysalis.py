"""Convert an HDF5 file to a Esperanto file"""

import os
import shutil
import logging
from ewokscore import Task
from fabio.app.eiger2crysalis import Converter
from fabio import esperantoimage

logger = logging.getLogger(__name__)


class Eiger2Crysalis(
    Task,
    input_names=["images", "processed_output", "output", "distance", "beam"],
    optional_input_names=[
        "energy",
        "wavelength",
        "polarization",
        "kappa",
        "alpha",
        "theta",
        "phi",
        "omega",
        "rotation",
        "transpose",
        "flip_ud",
        "flip_lr",
        "offset",
        "dry_run",
        "cal_mask",
        "dummy",
        "verbose",
        "debug",
        "list",
        "custom_frame_set_path",
    ],
    output_names=["output_path"],
):
    def run(self):
        args = self.inputs
        esperantoimage.EsperantoImage.DUMMY = args.dummy
        converter = Converter(args)
        converter.convert_all()
        converter.finish()
        if args.custom_frame_set_path:
            if os.path.exists(args.custom_frame_set_path):
                shutil.copy(
                    args.custom_frame_set_path,
                    os.path.join(os.path.dirname(args.output), "frame.set"),
                )
            else:
                logger.warning(f"File {args.custom_frame_set_path} not found")
        self.outputs.output_path = args.processed_output
