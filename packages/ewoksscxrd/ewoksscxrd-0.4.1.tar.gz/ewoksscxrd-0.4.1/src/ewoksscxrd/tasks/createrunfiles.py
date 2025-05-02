import os
import logging
from ewokscore import Task
from .utils import create_run_file

logger = logging.getLogger(__name__)


class createRunFiles(
    Task,
    input_names=["output", "run_parameters"],
    output_names=["saved_files_path"],
):
    def run(self):
        args = self.inputs
        saved_files = []
        scans = [
            [
                args.run_parameters,
            ],
        ]
        # Compute the destination basename using the provided logic.
        destination_basename = os.path.basename(args.output)
        destination_dir = os.path.dirname(args.output)
        destination = os.path.join(destination_dir, destination_basename)

        logger.info(
            f"Starting createRunFiles task for file: {destination_basename}.run"
        )
        logger.debug(f"Computed destination: {destination}")

        create_run_file(
            scans, destination_dir, destination_basename
        )  # This doesn't take the .run ext
        saved_files.append(destination + ".run")
        logger.info(f"Created {destination}.run")

        self.outputs.saved_files_path = saved_files
        logger.info(
            "createRunFiles task completed. Saved files: " + ", ".join(saved_files)
        )
