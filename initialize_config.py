import argparse
import logging
import os
import typing
from pathlib import Path


class Config:
    SCRIPT_PARENT_FOLDER: Path = Path(__file__).resolve().parent

    def __init__(self,
                 log_path: Path,
                 input_path: Path,
                 output_path: Path
                 # debug=False
                 ):
        self.input_path = input_path
        self.output_path = output_path
        self.log_path = log_path
        # self.DEBUG = debug

        """
        Check if the Path is under ~ for safety
        """

        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        self.logger = logging.getLogger('__name__')  # __main__
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s [%(levelname)s] %(message)s",
                            handlers=[
                                logging.FileHandler(log_path),
                                logging.StreamHandler()]
                            )


def parse_arguments():
    """
    1. create an ArgumentParser object
    2. add_arguments
    3. create a Namespace object `args` where to store the parsed arguments
    These are named after the long format (i.e. --input -> input)
    4. access the parameters under args.<argument>

    Folder paths, synchronization interval and log file path
    """

    # Parse the parameters from the parser object

    parser = argparse.ArgumentParser(
        description="A synchronization script.",
        add_help=True
    )
    parser.add_argument(
        "-i",
        "--input-path",
        type=Path,
        required=True,
        help='Input path.'
    )
    parser.add_argument(
        "-o",
        "--output-path",
        type=Path,
        required=True,
        help="Output path. This will be synchronized with the INPUT_PATH",
    )

    parser.add_argument(
        "-t",
        "--time-interval",
        type=int,
        required=True,
        help="Synchronization time interval in seconds.",

    )

    parser.add_argument(
        "-l",
        "--log-file-path",
        type=Path,
        default=".",
        required=True,
        help="Log file path.",
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Debug mode.")
    """
    Contains
    Namespace(input_path='asdf', output_path='asdf', time_interval=1, log_path='asdf', debug=False)

    """

    """
    Relative vs absolute paths?
    """
    return parser.parse_args()


def initialize_config():
    args = parse_arguments()
    return Config(log_path=args.log_file_path,
                  input_path=args.input_path,
                  output_path=args.output_path
                  )
