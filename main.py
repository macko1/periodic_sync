from init_config import initialize_config_and_logging
from periodic_sync import periodic_sync


def main():
    print("=== Periodic one-way synchronization ===")
    config = initialize_config_and_logging()
    try:
        config.logger.info(f"Running one-way folder synchronization periodically every {config.time_interval} seconds\n"
                           f"source folder: {config.input_path}\n"
                           f"target folder: {config.output_path}\n")
        periodic_sync(config)
    except KeyboardInterrupt:
        config.logger.info("=== Received SIGINT, exiting. ===")


if __name__ == '__main__':
    main()
