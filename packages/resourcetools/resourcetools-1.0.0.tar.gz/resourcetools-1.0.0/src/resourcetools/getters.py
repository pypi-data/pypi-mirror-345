import importlib.resources
from importlib.abc import Traversable

from . import state


class ResourceGetter:
    def __init__(self, subfolder: str) -> None:
        self.subfolder: str = subfolder

    def __call__(self, filename: str) -> Traversable:
        if state.resource_package is None:
            raise RuntimeError(
                "resourcetools.initialize() must be called "
                "before using resource getters"
            )
        return (
            importlib.resources.files(state.resource_package)
            / self.subfolder
            / filename
        )


Icon: ResourceGetter = ResourceGetter(subfolder="icons")
Translations: ResourceGetter = ResourceGetter(subfolder="translations")
Image: ResourceGetter = ResourceGetter(subfolder="images")
