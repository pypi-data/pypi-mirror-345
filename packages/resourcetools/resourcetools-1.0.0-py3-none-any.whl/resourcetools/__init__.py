from types import ModuleType

from . import state
from .getters import Icon, Image, Translations


def initialize(resource_package: ModuleType) -> None:
    state.resource_package = resource_package


__all__ = [
    "initialize",
    "Icon",
    "Translations",
    "Image",
]
