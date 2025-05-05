import argparse
import os
from pathlib import Path
from dar_backup.config_settings import ConfigSettings
from dar_backup.util import setup_logging, get_logger
from dar_backup.command_runner import CommandRunner
from dar_backup.manager import create_db


def run_installer(config_file: str, create_db_flag: bool):
    config_file = os.path.expanduser(os.path.expandvars(config_file))
    config_settings = ConfigSettings(config_file)

    # Set up logging based on the config's specified log file
    command_log = config_settings.logfile_location.replace("dar-backup.log", "dar-backup-commands.log")
    logger = setup_logging(
        config_settings.logfile_location,
        command_log,
        log_level="info",
        log_stdout=True,
    )
    command_logger = get_logger(command_output_logger=True)
    runner = CommandRunner(logger=logger, command_logger=command_logger)

    # Create directories listed in config
    for attr in ["backup_dir", "test_restore_dir", "backup_d_dir", "manager_db_dir"]:
        path = getattr(config_settings, attr, None)
        if path:
            dir_path = Path(path).expanduser()
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"Created directory: {dir_path}")
            else:
                print(f"Directory already exists: {dir_path}")

    # Optionally create databases
    if create_db_flag:
        for file in os.listdir(config_settings.backup_d_dir):
            backup_def = os.path.basename(file)
            print(f"Creating catalog for: {backup_def}")
            result = create_db(backup_def, config_settings, logger)
            if result == 0:
                print(f"✔️  Catalog created (or already existed): {backup_def}")
            else:
                print(f"❌ Failed to create catalog: {backup_def}")


def installer_main():
    parser = argparse.ArgumentParser(description="dar-backup installer")
    parser.add_argument("--config", required=True, help="Path to config file")
    parser.add_argument("--create-db", action="store_true", help="Create catalog databases")
    args = parser.parse_args()

    run_installer(args.config, args.create_db)


if __name__ == "__main__":
    installer_main()
