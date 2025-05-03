import os
import shutil
import logging
from ewokscore import Task

logger = logging.getLogger(__name__)


class createIniFiles(
    Task,
    input_names=["output", "ini_file"],
    output_names=["saved_files_path"],
):
    def run(self):
        args = self.inputs
        saved_files = []
        # Compute the destination basename using the provided logic.
        ext = os.path.splitext(args.ini_file)[-1].lower()
        destination_basename = os.path.basename(args.ini_file)
        destination_dir = os.path.dirname(args.output)
        destination = os.path.join(destination_dir, destination_basename)

        logger.info(f"Starting createIniFiles task for file: {args.ini_file}")
        logger.debug(f"Computed destination: {destination}")

        # Check if the file exists and that it is a .ini file.
        if not os.path.exists(args.ini_file):
            logger.warning(f"File {args.ini_file} not found")
        elif ext != ".ini":
            logger.warning(f"File {args.ini_file} is not a .ini file")
        else:
            shutil.copy(args.ini_file, destination)
            saved_files.append(destination)
            logger.info(f"Copied .ini file to {destination}")

        self.outputs.saved_files_path = saved_files
        logger.info(
            "createIniFiles task completed. Saved files: " + ", ".join(saved_files)
        )
