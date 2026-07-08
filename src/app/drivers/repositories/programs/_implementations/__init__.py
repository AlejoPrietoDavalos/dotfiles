from typing import Dict

from src.app.drivers.repositories.programs._implementations.arandr_repository import (
    ArandrRepository,
)
from src.app.drivers.repositories.programs._implementations.bspwm_repository import (
    BspwmRepository,
)
from src.app.drivers.repositories.programs._implementations.docker_repository import (
    DockerRepository,
)
from src.app.drivers.repositories.programs._implementations.fonts_repository import (
    FontsRepository,
)
from src.app.drivers.repositories.programs._implementations.kitty_repository import (
    KittyRepository,
)
from src.app.drivers.repositories.programs._implementations.nvidia_repository import (
    NvidiaRepository,
)
from src.app.drivers.repositories.programs._implementations.starship_repository import (
    StarshipRepository,
)
from src.app.drivers.repositories.programs._implementations.picom_repository import (
    PicomRepository,
)
from src.app.drivers.repositories.programs._implementations.playerctl_repository import (
    PlayerctlRepository,
)
from src.app.drivers.repositories.programs._implementations.polybar_repository import (
    PolybarRepository,
)
from src.app.drivers.repositories.programs._implementations.pulseaudio_repository import (
    PulseaudioRepository,
)
from src.app.drivers.repositories.programs._implementations.ranger_repository import (
    RangerRepository,
)
from src.app.drivers.repositories.programs._implementations.rofi_repository import (
    RofiRepository,
)
from src.app.drivers.repositories.programs._implementations.scrot_repository import (
    ScrotRepository,
)
from src.app.drivers.repositories.programs._implementations.sxhkd_repository import (
    SxhkdRepository,
)
from src.app.drivers.repositories.programs._implementations.thunar_repository import (
    ThunarRepository,
)
from src.app.drivers.repositories.programs._implementations.vscode_repository import (
    VscodeRepository,
)
from src.app.drivers.repositories.programs._implementations.xclip_repository import (
    XclipRepository,
)
from src.app.drivers.repositories.programs._implementations.xorg_repository import (
    XorgRepository,
)
from src.core.entities.program_config import ProgramName
from src.core.repositories.programs.program_repository import CoreProgramRepository


def get_program_repositories() -> Dict[ProgramName, CoreProgramRepository]:
    # FIXME: Ponerle un name a cada repo y usar eso en vez de hardcodear el name acá.
    return {
        "arandr": ArandrRepository(),
        "bspwm": BspwmRepository(),
        "docker": DockerRepository(),
        "fonts": FontsRepository(),
        "kitty": KittyRepository(),
        "starship": StarshipRepository(),
        "nvidia": NvidiaRepository(),
        "picom": PicomRepository(),
        "playerctl": PlayerctlRepository(),
        "polybar": PolybarRepository(),
        "pulseaudio": PulseaudioRepository(),
        "ranger": RangerRepository(),
        "rofi": RofiRepository(),
        "scrot": ScrotRepository(),
        "sxhkd": SxhkdRepository(),
        "thunar": ThunarRepository(),
        "vscode": VscodeRepository(),
        "xclip": XclipRepository(),
        "xorg": XorgRepository(),
    }
