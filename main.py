import argparse
import configparser
import initialize_config
import hashlib
from sync import run_sync
from initialize_config import initialize_config


def main():
    config = initialize_config()
    config.logger()
    exit(0)
    # run_sync()


if __name__ == '__main__':
    main()
