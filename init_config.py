import argparse
import logging
import os
from pathlib import Path


class Config:
    """
    Configuration object
    """

    def __init__(self,
                 input_path: Path,
                 output_path: Path,
                 time_interval: int,
                 log_path: Path
                 # debug=False
                 ):
        self.time_interval = time_interval
        self.input_path = Path(input_path)
        self.output_path = Path(output_path)
        self.log_path = log_path
        # self.DEBUG = debug

        """
        Init logging
        """
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        self.logger = logging.getLogger('__name__')
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

    :return: Parsed arguments
    """
    # Parse the parameters from the parser object

    parser = argparse.ArgumentParser(
        description="Periodically synchronizes a source folder '--input-path', to a target folder '--output-path'.",
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
        help="Output path. The contents of this path will be overwritten by content in the input path."
    )

    parser.add_argument(
        "-t",
        "--time-interval",
        type=int,
        required=True,
        help="Synchronization time interval (in seconds).",
    )

    parser.add_argument(
        "-l",
        "--log-file-path",
        type=Path,
        default=".",
        required=True,
        help="Log file path.",
    )
    # parser.add_argument(
    #     "-d", "--debug", action="store_true", help="Debug mode.")

    # while True:
    #     user_input = input('Are you sure these paths are correct? '
    #                        f'The data in the output path will be lost (Y/N): ').strip().lower()
    #     if user_input in ['y', 'n']:
    #         break  # Exit the loop if the input is valid
    #     else:
    #         print('Please enter Y or N.')  # Prompt the user to enter a valid option

    return parser.parse_args()


def initialize_config_and_logging():
    args = parse_arguments()

    """
    Check if the paths received from the CLI exist.
    """
    if not Path(args.input_path).exists():
        print(
            f"[ERROR] Input path '{args.input_path}' does not exist.\n"
            f"Use a valid path. Terminating.")
        exit(1)

    if not Path(args.output_path).exists():
        print(
            f"[ERROR] Output path '{args.output_path}' does not exist.\n"
            f"Use a valid path. Terminating.")
        exit(1)

    if not Path(args.log_file_path).parent.exists():
        print(
            f"[ERROR] Invalid path for the log file '{args.log_file_path}'.\n"
            f"Use a valid path. Terminating.")
        exit(1)

    """
    Create a configuration object
    """
    return Config(log_path=args.log_file_path,
                  input_path=args.input_path,
                  output_path=args.output_path,
                  time_interval=args.time_interval
                  )
