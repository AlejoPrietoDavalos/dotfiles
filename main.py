import argparse
from typing import cast

from src.app.drivers.repositories.logs import ConfigureLoggingRepository
from src.app.drivers.repositories.programs import (
    ProgramInstallerRepository,
    ProgramLoaderRepository,
)
from src.core.entities.program_config import ProgramName
from src.core.use_cases.program_actions import ProgramActions


def main() -> None:
    configure_logging_repo = ConfigureLoggingRepository()
    configure_logging_repo.configure(log_filename="main.log")

    program_loader_repo = ProgramLoaderRepository()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "install",
            "uninstall",
            "install-requirement",
            "uninstall-requirement",
            "install-files",
            "uninstall-files",
            "dirty_install_all_packages",
        ],
    )
    parser.add_argument("--program", choices=sorted(program_loader_repo.list_programs()))
    args = parser.parse_args()

    if args.action != "dirty_install_all_packages" and args.program is None:
        parser.error("--program is required for this action")

    actions = ProgramActions(
        program_loader_repo=program_loader_repo,
        program_installer_repo=ProgramInstallerRepository(),
    )
    actions.run(action=args.action, program=cast(ProgramName, args.program) if args.program else None)


if __name__ == "__main__":
    main()
