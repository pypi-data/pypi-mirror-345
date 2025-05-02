import os
import shutil
import logging
from ewokscore import Task

logger = logging.getLogger(__name__)


class createSetCcdFiles(
    Task,
    input_names=["output", "ccd_set_file"],
    output_names=["saved_files_path"],
):
    def run(self):
        args = self.inputs
        saved_files = []
        # Compute the destination basename using the provided logic.
        ext = os.path.splitext(args.ccd_set_file)[-1].lower()  # Expect .set or .ccd
        destination_basename = os.path.basename(args.output) + ext
        destination_dir = os.path.dirname(args.output)

        logger.info(f"Starting createSetCcdFiles task for file: {args.ccd_set_file}")

        # Check if the file exists and that it is either a .set or .ccd file.
        if not os.path.exists(args.ccd_set_file):
            logger.warning(f"File {args.ccd_set_file} not found")
        elif ext not in (".set", ".ccd"):
            logger.warning(f"File {args.ccd_set_file} is not a .set or .ccd file")
        else:
            destination = os.path.join(destination_dir, destination_basename)
            shutil.copy(args.ccd_set_file, destination)
            saved_files.append(destination)
            logger.info(f"Created {destination}")

        self.outputs.saved_files_path = saved_files
        logger.info(
            "createSetCcdFiles task completed. Saved files: " + ", ".join(saved_files)
        )
