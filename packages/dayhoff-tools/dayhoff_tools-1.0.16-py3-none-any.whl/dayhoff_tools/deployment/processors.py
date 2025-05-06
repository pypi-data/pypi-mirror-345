import logging
import os
import subprocess
import shlex
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Processor(ABC):
    """Processes data locally.  Abstract class for specific calculations.
    Takes in a single file and produces a single file or folder of outputs."""

    @abstractmethod
    def run(self, input_file: str) -> str:
        """Do the calculation, including reading from input_file
        and writing to output_file"""
        output_path = "output_file"

        return output_path


class BoltzPredictor(Processor):
    """Processor for running Boltz docking predictions.

    This class wraps the Boltz docking tool to predict protein structures
    from sequence data.
    """

    def __init__(self, num_workers: int, boltz_options: str | None = None):
        """Initialize the BoltzPredictor.

        Args:
            num_workers: Number of worker threads to use as a default.
                         This can be overridden if --num_workers is present
                         in boltz_options.
            boltz_options: A string containing additional command-line options
                           to pass to the Boltz predictor. Options should be
                           space-separated (e.g., "--option1 value1 --option2").
        """
        self.num_workers = num_workers
        self.boltz_options = boltz_options

    def run(self, input_file: str) -> str:
        """Run Boltz prediction on the input file.

        Constructs the command using the input file, default number of workers,
        and any additional options provided via `boltz_options`. If `--num_workers`
        is specified in `boltz_options`, it overrides the default `num_workers`.

        Args:
            input_file: Path to the input file containing sequences

        Returns:
            Path to the output directory created by Boltz

        Raises:
            subprocess.CalledProcessError: If Boltz prediction fails
        """
        # Determine expected output directory name
        input_base = os.path.splitext(os.path.basename(input_file))[0]
        expected_output_dir = f"boltz_results_{input_base}"
        logger.info(f"Expected output directory: {expected_output_dir}")

        # Start building the command
        cmd = ["boltz", "predict", input_file]

        # Parse additional options if provided
        additional_args = []
        num_workers_in_opts = False
        if self.boltz_options:
            try:
                parsed_opts = shlex.split(self.boltz_options)
                additional_args.extend(parsed_opts)
                if "--num_workers" in parsed_opts:
                    num_workers_in_opts = True
                    logger.info(
                        f"Using --num_workers from BOLTZ_OPTIONS: {self.boltz_options}"
                    )
            except ValueError as e:
                logger.error(f"Error parsing BOLTZ_OPTIONS '{self.boltz_options}': {e}")
                # Decide if we should raise an error or proceed without options
                # For now, proceed without the additional options
                additional_args = []  # Clear potentially partially parsed args

        # Add num_workers if not specified in options
        if not num_workers_in_opts:
            logger.info(f"Using default num_workers: {self.num_workers}")
            cmd.extend(["--num_workers", str(self.num_workers)])

        # Add the parsed additional arguments
        cmd.extend(additional_args)

        # Log the final command
        # Use shlex.join for safer command logging, especially if paths/args have spaces
        try:
            safe_cmd_str = shlex.join(cmd)
            logger.info(f"Running command: {safe_cmd_str}")
        except AttributeError:  # shlex.join is Python 3.8+
            logger.info(f"Running command: {' '.join(cmd)}")

        # Stream output in real-time
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        stdout = process.stdout
        if stdout:
            for line in iter(stdout.readline, ""):
                logger.info(f"BOLTZ: {line.rstrip()}")

        # Wait for process to complete
        return_code = process.wait()
        if return_code != 0:
            logger.error(f"Boltz prediction failed with exit code {return_code}")
            raise subprocess.CalledProcessError(return_code, cmd)

        logger.info(
            f"Boltz prediction completed successfully. Output in {expected_output_dir}"
        )
        return expected_output_dir
