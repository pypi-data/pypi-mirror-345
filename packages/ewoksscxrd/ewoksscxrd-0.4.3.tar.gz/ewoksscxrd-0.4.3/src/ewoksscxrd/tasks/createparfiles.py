import os
import logging
from ewokscore import Task
from .utils import create_par_file

logger = logging.getLogger(__name__)


class createParFiles(
    Task,
    input_names=["output", "par_file"],
    output_names=["saved_files_path"],
):
    def run(self):
        args = self.inputs
        saved_files = []
        # Compute the destination basename using the provided logic.
        ext = os.path.splitext(args.par_file)[-1].lower()
        destination_basename = os.path.basename(args.output) + ext
        destination_dir = os.path.dirname(args.output)
        destination = os.path.join(destination_dir, destination_basename)

        logger.info(f"Starting createParFiles task for file: {args.par_file}")
        logger.debug(f"Computed destination: {destination}")

        # Check if the file exists and that it is a .par file.
        if not os.path.exists(args.par_file):
            logger.warning(f"File {args.par_file} not found")
        elif ext != ".par":
            logger.warning(f"File {args.par_file} is not a .par file")
        else:
            logger.info(
                f"Creating par file using scans with destination basename '{destination_basename}'"
            )
            create_par_file(args.par_file, destination_dir, destination_basename)
            saved_files.append(destination)
            logger.info(f"Created {destination}")

        self.outputs.saved_files_path = saved_files
        logger.info(
            "createParFiles task completed. Saved files: " + ", ".join(saved_files)
        )
